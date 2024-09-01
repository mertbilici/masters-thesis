pragma solidity ^0.8.0;

import "./Registration.sol";

contract HashList {
    string[] public hashes;
    Registration public registrationContract;
    uint256 constant MAX_HASHES = 1000;

    constructor(address _registrationAddress) {
        registrationContract = Registration(_registrationAddress);
    }

    event HashAdded(bool success); // Event to emit the success status

    function getHashes() public view returns (string[] memory) {
        return hashes;
    }

    function addHash(string memory _hashValue, address _lightNode) public returns (bool) {
        // Check if the sender is an approved full node
        if (!registrationContract.isApprovedFullNode(msg.sender)) {
            emit HashAdded(false);
            return false; 
        }
        // Check if the light node is valid
        if (!registrationContract.isApprovedLightNode(_lightNode)) {
            emit HashAdded(false);
            return false; 
        }
        hashes.push(_hashValue);
        // Maintain FIFO logic
        if (hashes.length > MAX_HASHES) {
            string[] memory newHashes = new string[](MAX_HASHES);
            for (uint i = 0; i < MAX_HASHES; i++) {
                newHashes[i] = hashes[hashes.length - MAX_HASHES + i];
            }
            hashes = newHashes;
        }
        emit HashAdded(true);
        return true; 
    }
}