#-- IMPORTS --#
from web3 import Web3
#-- END OF IMPORTS --#

#-- INITIALISATION OF THE WEB3 INTERFACE & CONTRACT INFORMATION --#
def initializeWeb3():
    global w3
    w3 = Web3(Web3.HTTPProvider("http://192.168.0.15:8545")) # The IP Address of the Web3 Application - Local for testing
    hash_list_address = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512" # The ethereum address of the hashList contract
    registration_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3" # The ethereum address of the registration contract
    # ABI of the relevant contracts
    hashABI = '[{"inputs":[{"internalType":"address","name":"_registrationAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"success","type":"bool"}],"name":"HashAdded","type":"event"},{"inputs":[{"internalType":"string","name":"_hashValue","type":"string"},{"internalType":"address","name":"_lightNode","type":"address"}],"name":"addHash","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getHashes","outputs":[{"internalType":"string[]","name":"","type":"string[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"hashes","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"registrationContract","outputs":[{"internalType":"contract Registration","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'
    registrationABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"_candidateAddress","type":"address"}],"name":"addCandidateAdmin","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_nodeAddress","type":"address"},{"internalType":"enum Registration.NodeType","name":"_nodeType","type":"uint8"}],"name":"approveNode","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"candidateAdmins","outputs":[{"internalType":"address","name":"candidateAddress","type":"address"},{"internalType":"uint256","name":"count","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getAdmins","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getApprovedLightNodes","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_address","type":"address"}],"name":"isAdmin","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_nodeAddress","type":"address"}],"name":"isApprovedFullNode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_nodeAddress","type":"address"}],"name":"isApprovedLightNode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nodes","outputs":[{"internalType":"address","name":"nodeAddress","type":"address"},{"internalType":"enum Registration.NodeType","name":"nodeType","type":"uint8"},{"internalType":"bool","name":"approved","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_nodeAddress","type":"address"},{"internalType":"enum Registration.NodeType","name":"_nodeType","type":"uint8"}],"name":"registerAndApproveNode","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"enum Registration.NodeType","name":"_nodeType","type":"uint8"}],"name":"registerNode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"registeredNodes","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_nodeAddress","type":"address"}],"name":"removeNode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_adminAddress","type":"address"}],"name":"retireAdmin","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"retiringAdmins","outputs":[{"internalType":"address","name":"adminAddress","type":"address"},{"internalType":"uint256","name":"count","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    global hash_list_contract
    hash_list_contract = w3.eth.contract(address=hash_list_address, abi=hashABI)
    global registration_contract
    registration_contract = w3.eth.contract(address=registration_address, abi=registrationABI)
#-- END OF INITIALIZATION & CONTRACT INFORMATION --#

#-- FUNCTIONS --#
def registerNewNode(sourceAddress, nodeType):
    if nodeType == '1': # Light Node
        tx_receipt = registration_contract.functions.registerNode(1).transact({'from': sourceAddress})
    elif nodeType == '0': # Full Node
        tx_receipt = registration_contract.functions.registerNode(0).transact({'from': sourceAddress})
    return tx_receipt

def approveNewNode(newNodeAddress, nodeType, sourceAddress):
    tx_receipt = registration_contract.functions.approveNode(newNodeAddress, int(nodeType)).transact({'from': sourceAddress})
    return tx_receipt

def registerAndApproveNewNode(newNodeAddress, nodeType, sourceAddress):
    tx_receipt = registration_contract.functions.registerAndApproveNode(newNodeAddress, int(nodeType)).transact({'from': sourceAddress})
    return tx_receipt

def getAndSaveRecentHashes():
    hashes = hash_list_contract.functions.getHashes().call()
    # Save the hashes retrieved from hashList function to a text file
    with open("hashListFull.txt", "a") as appender:
        for hash_value in hashes:
            appender.write(hash_value + "\n")
    print("Recent hashes saved and database updated successfully!")

def sendNewHashToBlockchain(hashInput, sourceAddress, lightNodeAddress):
    tx_receipt = hash_list_contract.functions.addHash(hashInput, lightNodeAddress).transact({'from': sourceAddress})
    returnedVal = w3.eth.get_transaction_receipt(tx_receipt)['logs'][0]['data']
    result = str(returnedVal.hex())
    return result # True = Successful / False = Error

def removeNode(nodeAddress, sourceAddress):
    tx_receipt = registration_contract.functions.removeNode(nodeAddress).transact({'from': sourceAddress})
    return tx_receipt

def getListofAdmins(sourceAddress):
    adminsList =  registration_contract.functions.getAdmins().call({'from': sourceAddress})
    return adminsList

def addCandidateAdmin(candidateAddress, sourceAddress):
    tx_receipt = registration_contract.functions.addCandidateAdmin(candidateAddress).transact({'from': sourceAddress})
    return tx_receipt

def retireAdmin(retiringAdmin, sourceAddress):
    tx_receipt = registration_contract.functions.retireAdmin(retiringAdmin).transact({'from': sourceAddress})
    return tx_receipt

def sendTransaction(transactionData, sourceAddress, recipientAddress):
    tx_receipt = w3.eth.send_transaction({'to': recipientAddress, 'from': sourceAddress, 'data': transactionData})
    return tx_receipt

def getTransaction(tx_address):
    result = w3.eth.get_transaction(tx_address)
    return result

def getAndSaveTransactionData(startBlock, addressToSearch):
    # Retrieves transaction data that has hashes from a block range and saves it to a file.
    all_transaction_data = []
    endBlock = w3.eth.get_block_number()
    for block_num in range(startBlock, endBlock + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx['to'] == addressToSearch:
                all_transaction_data.append(tx['input'])

    with open('hashListFull.txt', 'a') as appender:
        for data in all_transaction_data:
            appender.write(str(data.hex()) + '\n')

    print("Transaction data saved to hashListFull.txt")

def isApprovedFullNode(nodeAddress):
    result = registration_contract.functions.isApprovedFullNode(nodeAddress).call()
    return result

def isApprovedLightNode(nodeAddress):
    result = registration_contract.functions.isApprovedLightNode(nodeAddress).call()
    return result

def setSourceAdmin(adminNo):
    if (adminNo in [0, 1, 2]):
        sourceAddress = str(w3.eth.accounts[adminNo])
        return sourceAddress
    else:
        print("For TESTING Admins can only be accounts 0, 1 or 2.\nSelecting 0th Account automatically")
        sourceAddress = str(w3.eth.accounts[0])
        return sourceAddress

###--- TO DO ---###
#def getListOfLightNodes():
    #tx_receipt = registration_contract.functions.getApprovedLightNodes().transact()
    #returnedVal = w3.eth.get_transaction_receipt(tx_receipt)['logs'][0]['data']
    #result = str(returnedVal.hex())
    #return result

###--- END OF TO DO ---###

#-- END OF FUNCTIONS --#
