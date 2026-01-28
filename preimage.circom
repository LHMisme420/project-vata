pragma circom 2.1.6;

include "node_modules/circomlib/circuits/poseidon.circom";

template PoseidonPreimageProof() {
    // Private input: the secret you know (e.g. a password or value)
    signal input secret;

    // Public output: the Poseidon hash commitment
    signal output commitment;

    component poseidon = Poseidon(1);
    poseidon.inputs[0] <== secret;

    commitment <== poseidon.out;
}

component main {public [commitment]} = PoseidonPreimageProof();
