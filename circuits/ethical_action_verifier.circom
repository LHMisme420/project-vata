pragma circom 2.1.5;

include "circomlib/poseidon.circom";
include "circomlib/comparators.circom";
include "circomlib/bitify.circom";
include "circomlib/merkleTree.circom";  // assuming you have or copy from circomlib

// Minimal ethical verifier
template EthicalActionVerifier(nLevels) {  // nLevels = Merkle tree depth, e.g. 5 for small tree

    // Public inputs
    signal input mandate_hash;      // Poseidon(ethics_charter.json content)
    signal input action_hash;       // Poseidon(proposed_action_string)
    signal input root;              // Merkle root of allowed action patterns or compliance flags

    // Private inputs
    signal input prompt[100];       // padded prompt words/hashes (simplified)
    signal input trace[50];         // reasoning steps hashed
    signal input action[50];        // action description words
    signal input path_elements[nLevels][2];  // Merkle proof siblings
    signal input path_index;        // index in tree

    // Components
    component poseidon_prompt = Poseidon(100);
    for (var i=0; i<100; i++) { poseidon_prompt.inputs[i] <== prompt[i]; }

    component poseidon_action = Poseidon(50);
    for (var i=0; i<50; i++) { poseidon_action.inputs[i] <== action[i]; }

    // Enforce action hash matches
    action_hash === poseidon_action.out;

    // Simple harm check: detect keywords (e.g., "bomb", "hack") via dummy constraint
    // In production: use string matching or hash lookup table
    signal harmful;
    harmful <== 0;  // placeholder: set to 1 if harmful detected (expand later)

    signal must_refuse;
    must_refuse <== harmful;  // if harmful → must refuse

    // Compliance bit: 1 if refused when needed
    signal compliance;
    compliance <== 1 - must_refuse;  // simplistic: pass if no harm or refused

    // Merkle proof that this compliance is allowed (e.g., under mandate root)
    component merkleProof = MerkleTreeInclusionProof(nLevels);
    merkleProof.leaf_index <== path_index;
    for (var i=0; i<nLevels; i++) {
        for (var j=0; j<2; j++) {
            merkleProof.siblings[i][j] <== path_elements[i][j];
        }
    }
    merkleProof.root <== root;
    merkleProof.leaf <== compliance;  // prove compliance bit is in tree

    // Mandate hash check (dummy for now)
    mandate_hash === mandate_hash;  // placeholder to include in public

    // Final public constraint
    signal dummy_out;
    dummy_out <== compliance * 1;
}

component main {public [mandate_hash, action_hash, root]} = EthicalActionVerifier(5);
