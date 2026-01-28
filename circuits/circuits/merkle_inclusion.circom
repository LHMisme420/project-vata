pragma circom 2.1.6;

include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/mux1.circom";
include "circomlib/circuits/bitify.circom";

// Optimized Poseidon Merkle tree inclusion proof
// ~8 000 constraints for 32 levels, path-only verification, left-right mux

template MerkleInclusion(levels) {
    signal input leaf;
    signal input pathElements[levels];
    signal input pathIndices[levels];   // 0 = left, 1 = right
    signal output root;

    component hashers[levels];
    component muxes[levels];
    component bits[levels];

    signal current;
    current <== leaf;

    for (var i = 0; i < levels; i++) {
        bits[i] = Num2Bits(1);
        bits[i].in <== pathIndices[i];

        muxes[i] = MultiMux1(2);
        muxes[i].c[0][0] <== current;
        muxes[i].c[0][1] <== pathElements[i];
        muxes[i].c[1][0] <== pathElements[i];
        muxes[i].c[1][1] <== current;
        muxes[i].s <== bits[i].out[0];

        hashers[i] = Poseidon(2);
        hashers[i].inputs[0] <== muxes[i].out[0];
        hashers[i].inputs[1] <== muxes[i].out[1];

        current <== hashers[i].out;
    }

    root <== current;
}

component main {public [root]} = MerkleInclusion(32);
