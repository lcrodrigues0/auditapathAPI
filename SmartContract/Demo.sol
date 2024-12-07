// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.0;

contract Demo {
    function Hello() public pure returns (string memory){
        return "Hello";
    }
    
    event Echo(string message);

    function echo(string calldata message) external {
        emit Echo(message);
    }
}