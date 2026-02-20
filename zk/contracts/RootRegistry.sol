// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RootRegistry {
    mapping(uint256 => bool) public isRoot;
    event RootAnchored(uint256 root, address indexed by);

    function anchorRoot(uint256 root) external {
        isRoot[root] = true;
        emit RootAnchored(root, msg.sender);
    }
}

