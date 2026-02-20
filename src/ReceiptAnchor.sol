// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ReceiptAnchor {

    event ReceiptAnchored(bytes32 indexed receiptHash, address indexed sender);

    mapping(bytes32 => bool) public anchored;

    function anchor(bytes32 receiptHash) external {
        require(!anchored[receiptHash], "Already anchored");
        anchored[receiptHash] = true;
        emit ReceiptAnchored(receiptHash, msg.sender);
    }

    function isAnchored(bytes32 receiptHash) external view returns (bool) {
        return anchored[receiptHash];
    }
}