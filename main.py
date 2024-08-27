"""
Malware detection software based on machine learning and blockchain
Prepared as a part of my Master's Thesis in Cyber Security Engineering @ University of Warwick
"""
#-- IMPORTS --#
import os
import sys
import time
import hashlib

from numpy.core.shape_base import block

import networkWeb3 as blockchain
#import matplotlib.pyplot as plt # Optional for vissualisation
#-- END OF IMPORTS --#

##-- DEBUGGING AND TESTING TOOLS & VARIABLES --##
testAddress1 = '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65'  # Test Account No.4 in Hardhat
testAddress2 = '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc'  # Test Account No.5 in Hardhat
testAddress3 = '0x976EA74026E726554dB657fA54763abd0C3a0aa9'  # Test Account No.6 in Hardhat
testAddress4 = '0x14dC79964da2C08b23698B3D3cc7Ca32193d9955'  # Test Account No.7 in Hardhat
##-- END OF DEBUGGING AND TESTING TOOLS & VARIABLES --##

#-- FUNCTIONS --#
def createFileHash(fileName):
    fileHash = ''
    if os.path.isfile(fileName):
        with open(fileName, 'rb') as f:
            fileNameRead = f.read()
            fileHash = hashlib.sha256(fileNameRead).hexdigest()
    else:
        print("ERROR: The given file cannot be found. Please check file name and ensure you use the full path!")
        time.sleep(3)
        startProgram()

    return fileHash

def checkForHashMatch(fileName):
    hashToLookFor = createFileHash(fileName)
    with open('hashListFull.txt', 'r') as localHashes:
        for row in localHashes:
            if hashToLookFor in row:
                return 0
    return 1

def scanFileML(fileToScan):
    """
    Send a request to the Machine Learning Backend and get the result.
    """
    scanResult = os.system(f"python Machine-Learning-Backend/ML-Backend.py {fileToScan}")
    return scanResult

def processFiles(path):
    """
    Iterate over multiple files in the given directory and feed them to the scanning function.
    Collect the results for further analysis.
    """
    try:
        allFiles = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        totalFiles = len(allFiles)
        numProcessedFiles = 0
        startIndex = 0
        results = []
        while startIndex < totalFiles:
            endIndex = min(startIndex + 1000, totalFiles) # Scan the next 1000 files (For development only)
            batchFiles = allFiles[startIndex:endIndex]
            for filename in batchFiles:
                if os.path.isfile(os.path.join(path, filename)):
                    filePath = os.path.join(path, filename)
                    result = scanFileML(filePath)
                    results.append(result)  # Store the result for each file
                    numProcessedFiles += 1
                    progress = numProcessedFiles / totalFiles
                    print(f"Progress: {progress:.3%}", end="\n") # On a new line looks better
            startIndex = endIndex
            if startIndex < totalFiles:
                while True:
                    confirmation = input("Scan next 1000 files? (y/n): ")
                    if confirmation.lower() in ('y', 'n'):
                        if confirmation.lower() == 'n':  # Break the outer loop only if 'n'
                            return results
                        break  # Break the inner loop for valid input
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
        return results
    except FileNotFoundError:
        print("The given directory cannot be found. Please ensure you use the full path!")
        return "Path Error"

def scanDirectoryHash(directoryPath):
    try:
        if not os.path.isdir(directoryPath):
            print("ERROR: The given directory cannot be found. Please check file name and ensure you use the full path!")
            time.sleep(3)
            error = ['ERROR']
            return [], error
        else:
            allFiles = [f for f in os.listdir(directoryPath) if os.path.isfile(os.path.join(directoryPath, f))]
            totalFiles = len(allFiles)
            numProcessedFiles = 0
            startIndex = 0
            results = []
            knownMalware = []
            print("Beginning hash lookup for the directory.")
            while startIndex < totalFiles:
                endIndex = min(startIndex + 1000, totalFiles)  # Scan the next 1000 files (For development only)
                batchFiles = allFiles[startIndex:endIndex]
                for filename in batchFiles:
                    if os.path.isfile(os.path.join(directoryPath, filename)):
                        filePath = os.path.join(directoryPath, filename)
                        result = checkForHashMatch(filePath)
                        if result ==0:
                            knownMalware.append(filename)
                        results.append(result)  # Store the result for each file
                        numProcessedFiles += 1
                        progress = numProcessedFiles / totalFiles
                        print(f"Progress: {progress:.3%}", end="\n")  # On a new line looks better
                startIndex = endIndex
                if startIndex < totalFiles:
                    while True:
                        confirmation = input("Scan next 1000 files? (y/n): ")
                        if confirmation.lower() in ('y', 'n'):
                            if confirmation.lower() == 'n':  # Break the outer loop only if 'n'
                                return results, knownMalware
                            break  # Break the inner loop for valid input
                        else:
                            print("Invalid input. Please enter 'y' or 'n'.")
            return results, knownMalware
    except FileNotFoundError:
        print("The given directory cannot be found. Please ensure you use the full path!")
        return "Path Error"

    except:
        return "Unknown Error"

def scanDirectoryML(directoryPath):
    try:
        results = processFiles(directoryPath) # Forward to directory scanning
        count_zeros = results.count(0)
        count_ones = results.count(1)
        total = len(results)
        print("Number of malicious files: " + str(count_zeros))
        print("Number of legitimate files: " + str(count_ones))
        ratio_ones = 100*(count_ones / total)
        ratio_zeros = 100*(count_zeros / total)
        print(f"Ratio of malicious files: {ratio_zeros:.4f}")
        print(f"Ratio of legitimate files: {ratio_ones:.4f}")
    except:
        return "Unknown Error"

    # -- Optional visualisation part - Creates a pie chart of scan results. Uncomment to activate --#
    # labels = ['TP', 'FN']
    # sizes = [ratio_zeros, ratio_ones]
    # fig, ax = plt.subplots()
    # ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=40)
    # ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart
    # plt.title('Ratio of True Positives and False Negatives')
    # plt.show()
#-- END OF FUNCTIONS --#

#-- MAIN FUNCTION --#
def main():
    startProgram()

def exitProgram():
    sys.exit(0)

def startProgram():
    print("-----------------------------------------------------\nWelcome to decentralized anti-malware  \nPlease select an option to begin:")
    print("1. Scan a single file")
    print("2. Scan a directory")
    print("3. See blockchain related operations")
    print("4. Exit\n")
    userSelection = int(input("Enter your selection : "))
    if (userSelection in [1,2,3,4]):
        if(userSelection == 1):
            fileInputSingle = input("Enter the path and name of the file : ")
            resultSingleHashMatch = checkForHashMatch(fileInputSingle)
            if resultSingleHashMatch == 0:
                print("The file " + fileInputSingle + " is a known malware")
            else:
                print("No matching hash found in local database. Proceeding to use Machine Learning to scan the file.")
                resultSingleML = scanFileML(fileInputSingle)
                print("The file " + fileInputSingle + " is a " + ["malware", "legitimate file", "not found"][resultSingleML])
            userInput = input("Would you like to return to main menu? (y/n) ")
            if not userInput.lower() in ('y', 'n'):
                print("Bad input\nExiting software.")
                time.sleep(4)
                exitProgram()
            else:
                if userInput.lower() == 'y':
                    startProgram()
                elif userInput.lower() == 'n':
                    exitProgram()

        elif(userSelection == 2):
            print("This will scan the first 1000 files in the directory and will ask to proceed after each 1000 files")
            directoryPath = input("Enter the path of the folder to process: ")
            resultDirectoryHashMatch, resultsKnownMalware = scanDirectoryHash(directoryPath)
            if resultsKnownMalware == ['ERROR']:
                exitProgram()
            elif resultsKnownMalware != []:
                for element in resultsKnownMalware:
                    print("These files are known malware:\n" + element)
            print("\nThe hash lookup ended. Now proceeding to the Machine Learning scan")
            scanDirectoryML(directoryPath)
            userInput = input("Would you like to return to main menu? (y/n) ")
            if not userInput.lower() in ('y', 'n'):
                print("Bad input\nExiting software.")
                time.sleep(4)
                exitProgram()
            else:
                if userInput.lower() == 'y':
                    startProgram()
                else:
                    exitProgram()

        elif (userSelection == 3):
            print("This menu is used for interactions with the blockchain.\nPlease select an option to continue:")
            print("1. Register a new node")
            print("2. Update local database with latest new hashes")
            print("3. Update local database with all hashes")
            print("4. Manually add a hash to the blockchain")
            print("5. Administrator-Only Operations")
            print("6. Return to the main menu")
            userSelection2 = int(input("Enter your selection : "))
            if (userSelection2 in [1, 2, 3, 4, 5]):
                blockchain.initializeWeb3()
                print("Blockchain initialization completed.")
                if (userSelection2 == 1):
                    nodeInput = input("Enter the node address to register : ")
                    nodeType = input("Enter the node type (Full=0, Light=1) : ")
                    tx_receipt = blockchain.registerNewNode(nodeInput, nodeType)
                    print("Transaction Receipt: " + str(tx_receipt))
                    userInput = input("Would you like to return to main menu? (y/n) ")
                    if not userInput.lower() in ('y', 'n'):
                        print("Bad input\nExiting software.")
                        time.sleep(4)
                        exitProgram()
                    else:
                        if userInput.lower() == 'y':
                            startProgram()
                        else:
                            exitProgram()

                elif (userSelection2 == 2):
                    blockchain.getAndSaveRecentHashes()
                    print("Connecting to the blockchain for latest hashes.")
                    userInput = input("Would you like to return to main menu? (y/n) ")
                    if not userInput.lower() in ('y', 'n'):
                        print("Bad input\nExiting software.")
                        time.sleep(4)
                        exitProgram()
                    else:
                        if userInput.lower() == 'y':
                            startProgram()
                        else:
                            exitProgram()

                elif (userSelection2 == 3):
                    print("Connecting to the blockchain for ALL hashes.")
                    startBlock = int(input("Enter the starting block for the search : "))
                    #lightNodeList = blockchain.getListOfLightNodes()
                    #lightNodeAddress = lightNodeList[0]
                    lightNodeAddress = input("Enter the light node address : ")
                    blockchain.getAndSaveTransactionData(startBlock, lightNodeAddress)
                    userInput = input("Would you like to return to main menu? (y/n) ")
                    if not userInput.lower() in ('y', 'n'):
                        print("Bad input\nExiting software.")
                        time.sleep(4)
                        exitProgram()
                    else:
                        if userInput.lower() == 'y':
                            startProgram()
                        else:
                            exitProgram()

                elif (userSelection2 == 4):
                    print("Use this function to manually add a hash to the recent hashes list")
                    hashToSend = input("Enter the hash to send : ")
                    fullNodeAddress = input("Enter the source node : ")
                    lightNodeAddress = input("Enter the target node : ")
                    resultOfSend = blockchain.sendNewHashToBlockchain(hashToSend, fullNodeAddress, lightNodeAddress)
                    if resultOfSend:
                        print("Hash sent successfully!")
                    else:
                        print("Error: Either the source or target node is not approved")
                    userInput = input("Would you like to return to main menu? (y/n) ")
                    if not userInput.lower() in ('y', 'n'):
                        print("Bad input\nExiting software.")
                        time.sleep(4)
                        exitProgram()
                    else:
                        if userInput.lower() == 'y':
                            startProgram()
                        else:
                            exitProgram()

                elif (userSelection2 == 5):
                    print("The operations on this list can only be called by an admin.\nPlease select an option to continue:")
                    print("1. Approve new node")
                    print("2. Register and approve a new node")
                    print("3. Remove a node from the system")
                    print("4. Get the list of all admins")
                    print("5. Vote for a candidate admin")
                    print("6. Vote for retiring an admin")
                    print("7. Return to the main menu")
                    userSelection3 = int(input("Enter your selection : "))
                    if (userSelection3 in [1, 2, 3, 4, 5, 6]):
                        adminSelection = int(input("Enter your desired admin number selection (Only 0,1,2 for Testing): "))
                        sourceAddress = blockchain.setSourceAdmin(adminSelection)
                        if (userSelection3 == 1):
                            nodeInput = input("Enter the node address to approve : ")
                            nodeType = input("Enter the node type (Full=0, Light=1) : ")
                            tx_receipt = blockchain.approveNewNode(nodeInput, nodeType, sourceAddress)
                            print("Transaction Receipt: " + str(tx_receipt))
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                        elif (userSelection3 == 2):
                            nodeInput = input("Enter the node address to register & approve : ")
                            nodeType = input("Enter the node type (Full=0, Light=1) : ")
                            tx_receipt = blockchain.registerAndApproveNewNode(nodeInput, nodeType, sourceAddress)
                            print("Transaction Receipt: " + str(tx_receipt))
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                        elif (userSelection3 == 3):
                            nodeInput = input("Enter the node address to remove : ")
                            tx_receipt = blockchain.removeNode(nodeInput, sourceAddress)
                            print("Transaction Receipt: " + str(tx_receipt))
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                        elif (userSelection3 == 4):
                            adminsList = blockchain.getListofAdmins(sourceAddress)
                            print("Addresses of the current admins:\n")
                            print(adminsList)
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                        elif (userSelection3 == 5):
                            nodeInput = input("Enter the node address to vote for candidate admin: ")
                            tx_receipt = blockchain.addCandidateAdmin(nodeInput, sourceAddress)
                            print("Transaction Receipt: " + str(tx_receipt))
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                        elif (userSelection3 == 6):
                            nodeInput = input("Enter the admin address to vote for retiring it: ")
                            tx_receipt = blockchain.retireAdmin(nodeInput, sourceAddress)
                            print("Transaction Receipt: " + str(tx_receipt))
                            userInput = input("Would you like to return to main menu? (y/n) ")
                            if not userInput.lower() in ('y', 'n'):
                                print("Bad input\nExiting software.")
                                time.sleep(4)
                                exitProgram()
                            else:
                                if userInput.lower() == 'y':
                                    startProgram()
                                else:
                                    exitProgram()

                    elif (userSelection3 == 7):
                        startProgram()

                    else:
                        print("Bad input\nExiting software.")
                        time.sleep(3)
                        exitProgram()

            elif (userSelection2 == 6):
                startProgram()

            else:
                print("Bad input\nExiting software.")
                time.sleep(3)
                exitProgram()

        else:
            exitProgram()

    else:
        print("Bad input\nExiting software.")
        time.sleep(4)
        exitProgram()
#-- END OF MAIN FUNCTION --#

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
