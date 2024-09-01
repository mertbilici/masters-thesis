pragma solidity ^0.8.0;

contract Registration {
    enum NodeType { FULL, LIGHT }

    struct Node {
        address nodeAddress;
        NodeType nodeType;
        bool approved;
    }

    struct CandidateAdmin {
        address candidateAddress;
        uint count;
        mapping(address => bool) voters; // Add the voters mapping here
    }

    struct RetiringAdmin {
        address adminAddress;
        uint count;
        mapping(address => bool) voters; // Add the voters mapping here
    }

    address[] internal admins; // Make admins array internal for better security
    address[] public registeredNodes;
    mapping(address => Node) public nodes;
    mapping(address => CandidateAdmin) public candidateAdmins;
    mapping(address => RetiringAdmin) public retiringAdmins;

    constructor() {
        // Add initial admins
        admins.push(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266); // Admin 1
        admins.push(0x70997970C51812dc3A010C7d01b50e0d17dc79C8); // Admin 2
        admins.push(0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC); // Admin 3
        // ... add more initial admins if needed
    }

    modifier onlyAdmin() {
        bool isAdmin = false;
        for (uint i = 0; i < admins.length; i++) {
            if (msg.sender == admins[i]) {
                isAdmin = true;
                break;
            }
        }
        require(isAdmin, "Not an admin");
        _;
    }

    // 1. New node calls for registration
    function registerNode(NodeType _nodeType) external returns (bool) {
        // Check if the node is already registered
        if (nodes[msg.sender].nodeAddress != address(0)) {
            return false; // Node is already registered
        }

        nodes[msg.sender] = Node(msg.sender, _nodeType, false);
        registeredNodes.push(msg.sender);

        return true; // Registration successful
    }

    // 2. Admin approves a new user
    function approveNode(address _nodeAddress, NodeType _nodeType) external onlyAdmin returns (uint8) {
        // Check if the node is registered (check if it's in the registeredNodes array)
        bool isRegistered = false;
        for (uint i = 0; i < registeredNodes.length; i++) {
            if (registeredNodes[i] == _nodeAddress) {
                isRegistered = true;
                break;
            }
        }
        require(isRegistered, "Node not registered");

        // Check if the node is already approved
        if (nodes[_nodeAddress].approved) {
            return 1; // Node already approved
        }

        nodes[_nodeAddress].nodeType = _nodeType;
        nodes[_nodeAddress].approved = true;
        return 2; // Node approved successfully
    }

    // 3. Admin directly registers and approves a new node
    function registerAndApproveNode(address _nodeAddress, NodeType _nodeType) external onlyAdmin {
        nodes[_nodeAddress] = Node(_nodeAddress, _nodeType, true);
    }

    // Add a new candidate admin
    function addCandidateAdmin(address _candidateAddress) external onlyAdmin returns (uint) {
        // Check if the admin has already voted for this candidate
        if (candidateAdmins[_candidateAddress].voters[msg.sender]) {
            return 0; // Admin has already voted for this candidate
        }

        if (candidateAdmins[_candidateAddress].count == 0) {
            // Initialize the count for the new candidate admin
            candidateAdmins[_candidateAddress].count = 1;
        } else {
            candidateAdmins[_candidateAddress].count++;
        }

        // Mark the admin as having voted for this candidate
        candidateAdmins[_candidateAddress].voters[msg.sender] = true;

        if (candidateAdmins[_candidateAddress].count == 3) {
            admins.push(_candidateAddress);
            delete candidateAdmins[_candidateAddress];
            return 3;
        } else {
            return candidateAdmins[_candidateAddress].count;
        }
    }

    // Initiate admin retirement process
    function retireAdmin(address _adminAddress) external onlyAdmin returns (uint8) {
        require(isAdmin(_adminAddress), "Not an admin");

        // Check if the admin has already voted for this retiring admin
        if (retiringAdmins[_adminAddress].voters[msg.sender]) {
            return 0; // Admin has already voted for this retiring admin
        }

        if (retiringAdmins[_adminAddress].count == 0) {
            // Initialize the count for the new retiring admin
            retiringAdmins[_adminAddress].count = 1;
        } else {
            retiringAdmins[_adminAddress].count++;
        }

        // Mark the admin as having voted for this retiring admin
        retiringAdmins[_adminAddress].voters[msg.sender] = true;

        if (retiringAdmins[_adminAddress].count == 3) {
            removeAdmin(_adminAddress);
            delete retiringAdmins[_adminAddress];
            return 3; // Admin removed
        } else {
            return 1; // Retiring admin added (count incremented)
        }
    }

    // Internal function to remove an admin
    function removeAdmin(address _adminAddress) internal {
        for (uint i = 0; i < admins.length; i++) {
            if (admins[i] == _adminAddress) {
                admins[i] = admins[admins.length - 1];
                admins.pop();
                break;
            }
        }
    }

    // Helper function to check if an address is an admin
    function isAdmin(address _address) public view returns (bool) {
        for (uint i = 0; i < admins.length; i++) {
            if (admins[i] == _address) {
                return true;
            }
        }
        return false;
    }

    // Get the list of admins (only callable by admins)
    function getAdmins() external view onlyAdmin returns (address[] memory) {
        return admins;
    }

    // Helper function to check if a node is a full node and approved
    function isApprovedFullNode(address _nodeAddress) public view returns (bool) {
        return nodes[_nodeAddress].nodeType == NodeType.FULL && nodes[_nodeAddress].approved;
    }

    // Helper function to check if a node is a light node and approved
    function isApprovedLightNode(address _nodeAddress) public view returns (bool) {
        return nodes[_nodeAddress].nodeType == NodeType.LIGHT && nodes[_nodeAddress].approved;
    }

    // Helper function to get all approved light nodes
    function getApprovedLightNodes() public view returns (address[] memory) {
        uint count = 0;
        for (uint i = 0; i < registeredNodes.length; i++) { // Iterate over the registeredNodes array
            address nodeAddress = registeredNodes[i];
            if (nodes[nodeAddress].nodeType == NodeType.LIGHT && nodes[nodeAddress].approved) {
                count++;
            }
        }

        address[] memory lightNodes = new address[](count);
        uint index = 0;
        for (uint i = 0; i < registeredNodes.length; i++) {
            address nodeAddress = registeredNodes[i];
            if (nodes[nodeAddress].nodeType == NodeType.LIGHT && nodes[nodeAddress].approved) {
                lightNodes[index] = nodeAddress;
                index++;
            }
        }
        return lightNodes;
    }

    // Remove a node (only callable by admins)
    function removeNode(address _nodeAddress) external onlyAdmin returns (bool) {
        // Check if the node is registered
        require(nodes[_nodeAddress].nodeAddress == _nodeAddress, "Node not registered");
        // Remove the node from the mapping and registeredNodes array
        delete nodes[_nodeAddress];
        for (uint i = 0; i < registeredNodes.length; i++) {
            if (registeredNodes[i] == _nodeAddress) {
                registeredNodes[i] = registeredNodes[registeredNodes.length - 1];
                registeredNodes.pop();
                break;
            }
        }
        return true; // Indicate success
    }
}