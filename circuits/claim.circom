pragma circom 2.1.7;

template Claim() {
    signal input claimHash;  // public

    // A trivial self-constraint so it's "used"
    claimHash === claimHash;
}

component main { public [claimHash] } = Claim();