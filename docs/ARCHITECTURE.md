# VATA Protocol v2 — Architecture

User Data
   |
   v
Merkle Tree
   |
   v
Merkle Root --------------------+
   |                             |
   |                             v
Groth16 Circuit            L2 Anchor Registry
   |                             |
   v                             |
Witness -----------------> Proof + Public
                                   |
                                   v
                        Groth16 Verifier (ARB / OP)
                                   |
                                   v
                              TRUE / FALSE