pragma circom 2.1.5;

template EthicsCheck() {
    signal input action_score;      // Private: the agent's internal score
    signal input max_harm;          // Public: threshold from charter
    signal output compliant;        // 1 if OK, 0 if violation

    // Constraint: action_score <= max_harm
    component lt = LessThan(252);
    lt.in[0] <== action_score;
    lt.in[1] <== max_harm + 1;
    compliant <== lt.out;
}

component main {public [max_harm]} = EthicsCheck();
