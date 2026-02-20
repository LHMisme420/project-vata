FILE:        .\epoch_leaves.txt
SHA256:      0x2c7ee357520ec786f741a77fa90881620735301d751c791a79c01816e3ebfac8
CONTRACT:    0xC48A65E83999117c0F169b9d12120c172d3cE4e3
RPC:         https://ethereum-sepolia-rpc.publicnode.com
BATCH:       merkle\batches\claim_20260220_023031

Verify:
cast call 0xC48A65E83999117c0F169b9d12120c172d3cE4e3 "isAnchored(bytes32)(bool)" 0x2c7ee357520ec786f741a77fa90881620735301d751c791a79c01816e3ebfac8 --rpc-url https://ethereum-sepolia-rpc.publicnode.com
