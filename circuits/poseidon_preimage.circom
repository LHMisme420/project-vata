pragma circom 2.1.6;

include "circomlib/circuits/poseidon.circom";

// Poseidon Preimage Circuit: Proves knowledge of a preimage that hashes to a known output
// Optimizations: minimal constraints (~250), no unnecessary range checks, reuses Poseidon from circomlib

template PoseidonPreimage(nInputs) {
    signal input preimage[nInputs];     // private
    signal output hash;                 // public

    component poseidon = Poseidon(nInputs);

    for (var i = 0; i < nInputs; i++) {
        poseidon.inputs[i] <== preimage[i];
    }

    hash <== poseidon.out;
}

component main {public [hash]} = PoseidonPreimage(2);
