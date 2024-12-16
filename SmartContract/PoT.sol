// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.17 <0.9.0;

contract ProofOfTransit{

    /* DEV SETTINGS */

    address private controller;
    address private egress_edge;
    string private current_routeID;
    
    mapping(string => string) public probHash;
    mapping(string => logStructure) public route_id_audit;

    struct logStructure{
        uint probeFailAmount;
        uint probeNullAmount;
        uint probeSuccessAmount;
    }

    struct pastRouteConfig {
        string route_id;
        address egress_edge;
        uint last_timestamp;
    }

    pastRouteConfig[] public routeIdHistory;

    event ControllerSet(address indexed oldController, address indexed newController);

    modifier isController(address senderAddr) {
        require(senderAddr == controller, "Caller is not controller");
        _;
    }

    modifier isEgressEdge(address senderAddr) {
        require(senderAddr == egress_edge, "Caller is not egress edge");
        _;
    }

    
    constructor(address controllerAddr, address egress_edgeAddr,string memory routeId) {
        
        route_id_audit[routeId].probeFailAmount = 0;
        route_id_audit[routeId].probeSuccessAmount = 0;
        route_id_audit[routeId].probeNullAmount = 0;

        controller = controllerAddr;
        egress_edge = egress_edgeAddr;
        current_routeID = routeId;
        routeIdHistory.push(pastRouteConfig(routeId,egress_edgeAddr,block.timestamp));
        
        emit ControllerSet(address(0), controller);
    }


    /* POT FUNCTIONS */
    function changeController(address newController, address senderAddr) public isController(senderAddr) {
        emit ControllerSet(controller, newController);
        controller = newController;
    }

    function changeRouteIdAndEgressEdge(string memory newRouteId,address newEgressEdge, address senderAddr) public isController(senderAddr) {
        routeIdHistory.push(pastRouteConfig(newRouteId,newEgressEdge,block.timestamp));
        current_routeID = newRouteId;
        egress_edge = newEgressEdge;
    }

    function getController() external view returns (address) {
        return controller;
    }

    function setProbeHash(string memory id_x, string memory hash, address senderAddr) public isController(senderAddr) {
        probHash[id_x] = hash;
    }

    event ProbeFail();

    function logProbe(string memory id_x,string memory sig, address senderAddr) public isEgressEdge(senderAddr){
        if (compareStrings(probHash[id_x],"")) {
            route_id_audit[current_routeID].probeNullAmount += 1;
        } else if (compareStrings(probHash[id_x],sig)){
            route_id_audit[current_routeID].probeSuccessAmount += 1;
        } else {
            route_id_audit[current_routeID].probeFailAmount += 1;
            emit ProbeFail();
        }
    }

    function getCompliance() public view returns (uint,uint,uint) {
        return (route_id_audit[current_routeID].probeSuccessAmount,route_id_audit[current_routeID].probeFailAmount,route_id_audit[current_routeID].probeNullAmount);
    }


    /* AUX FUNCTIONS */
    function compareStrings(string memory a, string memory b) internal pure returns (bool) {
        return (keccak256(abi.encodePacked((a))) == keccak256(abi.encodePacked((b))));
    }

}

contract PoTFactory{

    mapping(string => ProofOfTransit) private flowPOT;
    mapping(string => address) public flowAddr;

    event Echo(string message);

    function echo(string calldata message) external {
        emit Echo(message);
    }

    function newFlow(string memory flowId, address egress_edgeAddr, string memory routeId) public{
        ProofOfTransit new_pot = new ProofOfTransit(msg.sender,egress_edgeAddr,routeId);

        flowPOT[flowId] = new_pot;
        flowAddr[flowId] = address(new_pot);
    }

    function setFlowProbeHash(string memory flowId, string memory id_x, string memory hash) public{
        ProofOfTransit pot = ProofOfTransit(flowPOT[flowId]);
        
        pot.setProbeHash(id_x,hash,msg.sender);
    }

    function logFlowProbeHash(string memory flowId, string memory id_x, string memory hash) public{
        ProofOfTransit pot = ProofOfTransit(flowPOT[flowId]);
        
        pot.logProbe(id_x,hash,msg.sender);
    }


    function setRouteId(string memory flowId,string memory newRouteID, address newEgressEdge) public{
        ProofOfTransit pot = ProofOfTransit(flowPOT[flowId]);
        
        pot.changeRouteIdAndEgressEdge(newRouteID,newEgressEdge,msg.sender);
    }


    function getFlowCompliance(string memory flowId) public view returns (uint success, uint fail, uint nil){
        ProofOfTransit pot = ProofOfTransit(flowPOT[flowId]);

        (success, fail, nil) = pot.getCompliance();

        return (success, fail, nil);

    }

}