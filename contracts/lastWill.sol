// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.7.0 <0.9.0;

contract Timed_Will {
    uint256 public totalFunds;
    uint256 public deadLine;
    uint256 public lastLive;
    uint256 public nextLive;
    uint256 public liveInterval;
    address public owner;
    address payable public contractAddress;

    // address payable[] public recipent;
    // mapping(address => uint256) public recipentAmount;

    struct Recipent {
        address payable reciAddress;
        uint receivePercentage;
    }

    // mapping(address => Recipent) public recipents;
    Recipent[] public recipents;

    event DeadlineConfirmed(address indexed from);
    event CheckIn(address indexed from, uint256 nextLive);
    event FundReceived(address indexed from, uint funds);

    constructor(uint timeLimit, uint interval, address payable[] memory sendTo, uint[] memory sendPercentage) {
        owner = msg.sender;
        totalFunds = 0;
        deadLine = timeLimit;
        lastLive = block.timestamp;
        liveInterval = interval;
        nextLive = lastLive + interval;
        contractAddress = payable(address(this));
        // recipent = sendTo;


        for (uint i=0; i<sendPercentage.length; i++){
            recipents.push(Recipent({
            reciAddress: sendTo[i],
            receivePercentage: sendPercentage[i]}));

        }

    }


    function getFund() public view returns (uint256){
        return totalFunds;
    }
    function getTime() public view returns (uint256){
        return deadLine;
    }

    function getTimeNow() public view returns (uint256){
        return block.timestamp;
    }
    function addFund(uint256 funds) private{
        require(msg.sender == owner,
        "Only contract creator can add fund to this contract.");
        totalFunds += funds;
        emit FundReceived(msg.sender, funds);
    }

    function confirmLive() public {
        /* require(msg.sender == owner,
        "Only contract creator can confirm live status."); */
        lastLive = block.timestamp;
        nextLive = lastLive + liveInterval;
        emit CheckIn(msg.sender, nextLive);
    }

    function isDeadLine() public view returns (bool){
        return (block.timestamp > deadLine);
    }

    function isPastLive() public view returns (bool){
        return (block.timestamp > (lastLive + liveInterval)); //time period for each live status
    }

    function Deadline() public{
        // anyone can check whether this contract have reach its deadlines
        if (isDeadLine() || isPastLive()){
             for (uint j=0; j<recipents.length; j++){
                 bool sent = recipents[j].reciAddress.send( percentile(totalFunds, recipents[j].receivePercentage) );
                 require(sent, "failed to send ether");
             }
                 // pecentage is an integer

        }
        emit DeadlineConfirmed(msg.sender);
    }

    function percentile(uint number, uint percent) private pure returns (uint){
        return (number * percent) / 100;
    }

    /* function setTime(uint time) public{
        // test function, remove on release
        deadLine = time;
    } */


    receive () external payable {addFund(msg.value);}
    fallback () external payable {}




}
