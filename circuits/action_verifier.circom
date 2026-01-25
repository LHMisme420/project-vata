
pragma circom 2.1.0;

include "circomlib/comparators.circom"; // Download circomlib: https://github.com/iden3/circomlib

template ActionVerifier() {
    signal input actionScore; // Agent's action impact (e.g., 0-100)
    signal input ethicsThreshold; // Charter rule (e.g., 10 for max allowed harm)
    signal output isCompliant;

    // Use LessThan template (handles up to 252 bits)
    component lt = LessThan(8); // 8 bits for small numbers; adjust as needed
    lt.in[0] <== actionScore;
    lt.in[1] <== ethicsThreshold;
    
    isCompliant <== lt.out; // 1 if actionScore < ethicsThreshold, else 0
}

component main {public [ethicsThreshold]} = ActionVerifier();

/* INPUT = {
    "actionScore": "5",
    "ethicsThreshold": "10"
} */
