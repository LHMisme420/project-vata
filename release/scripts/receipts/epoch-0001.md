# VATA Epoch 0001

Root:
0x939cda44d4e1b686504e55e3d4a04a6597cc056978e7b85a6e649d60385512aa

---

## Optimism Sepolia
Registry: 0xe0C202DF9D1d0187d84f4b94c8966cA6CD9c4d8e  
Anchor Tx: 0x2b4ea282ba531820562bcb4394f4307265f0e770e72d8975d770d379ab5ee6c5  

Verify:
cast call 0xe0C202DF9D1d0187d84f4b94c8966cA6CD9c4d8e "isRoot(uint256)(bool)" 0x939cda44d4e1b686504e55e3d4a04a6597cc056978e7b85a6e649d60385512aa --rpc-url https://sepolia.optimism.io  
Result: true

---

## Arbitrum Sepolia
Registry: 0x1a88C73407e349F91E5C1DDb03e1300d24e2cC35  
Anchor Tx: 0x69c4383761e4c6dbff4926b30afea1896371c22bec1f27b72f28de8a8dbb38fa  

Verify:
cast call 0x1a88C73407e349F91E5C1DDb03e1300d24e2cC35 "isRoot(uint256)(bool)" 0x939cda44d4e1b686504e55e3d4a04a6597cc056978e7b85a6e649d60385512aa --rpc-url https://sepolia-rollup.arbitrum.io/rpc  
Result: true
