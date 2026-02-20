// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ImmutableAnchor
/// @notice Append-only anchor for bytes32 roots. No owner, no upgrades, no admin.
///         Emits RootAnchored the first time a root is seen.
contract ImmutableAnchor {
    event RootAnchored(bytes32 indexed root, address indexed sender);

    mapping(bytes32 => bool) private _isRoot;

    function anchorRoot(bytes32 root) external {
        if (_isRoot[root]) return;
        _isRoot[root] = true;
        emit RootAnchored(root, msg.sender);
    }

    function isRoot(bytes32 root) external view returns (bool) {
        return _isRoot[root];
    }
}