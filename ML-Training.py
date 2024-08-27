"""
Used only for training new machine learning models
"""
#-- IMPORTS --#
import pandas
import numpy as np
import pickle
import joblib
import sklearn.ensemble as ens
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
#-- END OF IMPORTS --#

seed = 3195567  # Set seed to get accurate results over different trials
np.random.seed(seed)

#-- DATA PREPROCESSING --#
dataset = pandas.read_csv('Dataset/trainingData.csv', sep='|', low_memory=False) # Read data
X = dataset.drop(['Name','md5','legitimate'],axis=1).values # Drop columns that are not numeric and is our target.
Y = dataset['legitimate'].values
extraTrees = ens.ExtraTreesClassifier().fit(X, Y) # A prefitting is applied for the selection model
selectionModel = SelectFromModel(extraTrees, prefit=True) # Feature selection model
X_2 = selectionModel.transform(X)  # Reduce X to the selected features only
newFeatures = X_2.shape[1] # Number of selected features
#-- Split data as training and test--#
X_train, X_test, Y_train, Y_test = train_test_split(X_2, Y, test_size=0.3, stratify = Y, random_state=seed)
#-- Keep the list of reduced features used for training--#
features = []
index = np.argsort(extraTrees.feature_importances_)[::-1][:newFeatures]
for f in range(newFeatures):
    print("%d. Feature: %s (%f)" % (f + 1, dataset.columns[2+index[f]], extraTrees.feature_importances_[index[f]]))
    features.append(dataset.columns[2+f])
#-- END OF PREPROCESSING --#

#-- MODEL CREATION --#
model = { "DecisionTree":tree.DecisionTreeClassifier(max_depth=100),
         "RandomForest1":ens.RandomForestClassifier(n_estimators=44),
         "RandomForest2":ens.RandomForestClassifier(max_depth=24, n_estimators=44, max_features=4, min_samples_split=2),
#          "Adaboost":ens.AdaBoostClassifier(n_estimators=500),
#          "GradientBoosting":ens.GradientBoostingClassifier(n_estimators=500),
#          "GNB":GaussianNB(),
#          "LinearRegression":LinearRegression(),
#          "KNN":neighbors.KNeighborsClassifier(n_neighbors=26, weights='distance'),
#          "SVM":SVC(kernel='rbf', C=10, gamma=1),
#          "Neural":MLPClassifier(solver='sgd', alpha=1e-5, random_state=1)
}

#-- Pipelined SVM training + scoring (This one is much faster than above method for SVM)--#
#clfSVM = SVC(verbose=True)
#clfSVM = Pipeline(steps=[('scale', StandardScaler()), ('model', SVC(verbose=True, C=10, gamma=1, kernel='rbf'))] )
#param_grid = {
#    'model__C': [0.1, 1, 10],
#    'model__kernel': ['linear', 'rbf'],
#    'model__gamma': [0.1, 1]
#}
#grid_search = GridSearchCV(clfSVM, param_grid, cv=5, scoring='accuracy', verbose=2)
#grid_search.fit(X_train, Y_train)
#print("Best parameters:", grid_search.best_params_)
#print("Best Score:", grid_search.best_score_)
#clfSVM.fit(X_train,Y_train)
#scoreSVM = clfSVM.score(X_test, Y_test)
#print ('SVM : '+ str(scoreSVM))
#-- End of pipelined SVM training and rating --#

#-- Random Forest Training + Scoring ( Further trials for the best model)--#
clfRandom = ens.RandomForestClassifier()
param_grid2 = {
    'n_estimators': [10,44,50,100,1000],
    'min_samples_split': [2],
    'max_features': [4],
    'max_depth': [24]
}
grid_search2 = GridSearchCV(clfRandom, param_grid2, cv=5, scoring='roc_auc', verbose=3)
grid_search2.fit(X_train, Y_train)
print("Best parameters:", grid_search2.best_params_)
print("Best Score:", grid_search2.best_score_)
best_grid2 = grid_search2.best_estimator_
best_score2 = best_grid2.score(X_test, Y_test)
print("Best Score2:", best_score2)
#-- End of Random Forest Training --#

#-- MODEL EVALUATION --#
results = {}
for algo in model:
    clf = model[algo]
    clf.fit(X_train,Y_train)
    score = clf.score(X_test, Y_test)
    print ("%s : %s " %(algo, score))
    results[algo] = score
winner = max(results, key=results.get)
print(winner)
#-- Saving the final model and features for Random Forest and others --#
#joblib.dump(model[winner],'Machine-Learning-Model/classifier.pkl')
joblib.dump(clfRandom, 'Machine-Learning-Model/classifier.pkl')
open('Machine-Learning-Model/features.pkl', 'wb').write(pickle.dumps(features))
#-- Prediction and Results for the final model --#
#clf = model[winner]
clf = clfRandom
res = clf.predict(X_2)
mt = confusion_matrix(Y, res)
print("False positive rate : %f %%" % ((mt[0][1] / float(sum(mt[0])))*100))
print('False negative rate : %f %%' % ( (mt[1][0] / float(sum(mt[1]))*100)))
#-- END OF MODEL EVALUATION --#