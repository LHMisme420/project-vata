Spoofing: Fake proofs → mitigated by Groth16 soundness (assuming trusted setup).
Tampering: Ethics charter changes → git provenance + version control.
Info Disclosure: Secrets in code → guardian scans.
Denial of Service: Slow proof gen → future rate-limiting.
Elevation of Privilege: Agent bypasses ethics → ZK proof enforcement (but circuit bugs = risk).
Highlight top risks: under-constrained circuits (common in Circom → invalid proofs pass), trusted setup risks (Groth16), side-channel in witness gen.
