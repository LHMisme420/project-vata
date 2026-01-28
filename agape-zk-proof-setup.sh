#!/usr/bin/env bash

# =============================================================================
# Agape ZK Preimage Proof - Single-File Setup & Run
# Proves you know a secret whose Poseidon hash matches a public commitment
# Goal: sub-1s prove time in snarkjs Groth16 (consumer laptop)
# Author vibe: Leroy Preimage - agape flavor 🔥
# =============================================================================

set -e

echo "============================================================="
echo "  Agape ZK Preimage Proof - One-File Setup & Run"
echo "  Proving knowledge of secret → Poseidon hash (sub-1s target)"
echo "============================================================="

# ─────────────────────────────────────────────────────────────────────────────
# 1. Check/install dependencies
# ─────────────────────────────────────────────────────────────────────────────

command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Install from https://nodejs.org"; exit 1; }
command -v npm  >/dev/null 2>&1 || { echo "npm is required but not found."; exit 1; }
command -v circom >/dev/null 2>&1 || { echo "circom not found. Install: https://docs.circom.io/getting-started/installation/"; exit 1; }
command -v snarkjs >/dev/null 2>&1 || echo "Installing snarkjs globally..."; npm install -g snarkjs

# Install circomlib locally for the include
if [ ! -d "node_modules/circomlib" ]; then
  echo "Installing circomlib..."
  npm init -y >/dev/null 2>&1
  npm install circomlib
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. Create circuit file
# ─────────────────────────────────────────────────────────────────────────────

cat > preimage.circom << 'EOF'
pragma circom 2.1.6;

include "node_modules/circomlib/circuits/poseidon.circom";

template PoseidonPreimageProof() {
    signal input secret;
    signal output commitment;

    component poseidon = Poseidon(1);
    poseidon.inputs[0] <== secret;
    commitment <== poseidon.out;
}

component main {public [commitment]} = PoseidonPreimageProof();
EOF

echo "→ Circuit created: preimage.circom"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Create example input
# ─────────────────────────────────────────────────────────────────────────────

cat > input.json << 'EOF'
{
  "secret": "20260128agapelove"
}
EOF

echo "→ Input created: input.json (secret = 20260128agapelove)"

# ─────────────────────────────────────────────────────────────────────────────
# 4. Download small powers-of-tau (fast for tiny circuit)
# ─────────────────────────────────────────────────────────────────────────────

PTAU="powersOfTau28_hez_final_10.ptau"
if [ ! -f "$PTAU" ]; then
  echo "Downloading small ptau file..."
  curl -L -o "$PTAU" https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_10.ptau
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Compile circuit
# ─────────────────────────────────────────────────────────────────────────────

echo "Compiling circuit..."
circom preimage.circom --r1cs --wasm --sym -o .

# ─────────────────────────────────────────────────────────────────────────────
# 6. Trusted setup
# ─────────────────────────────────────────────────────────────────────────────

echo "Running Groth16 setup..."
snarkjs groth16 setup preimage.r1cs "$PTAU" preimage_0000.zkey

echo "Contributing entropy (Leroy Preimage - agape flavor 🔥)..."
snarkjs zkey contribute preimage_0000.zkey preimage_final.zkey --name="Leroy Preimage - agape flavor 🔥" -v

echo "Exporting verification key..."
snarkjs zkey export verificationkey preimage_final.zkey verification_key.json

# ─────────────────────────────────────────────────────────────────────────────
# 7. Generate proof & verify
# ─────────────────────────────────────────────────────────────────────────────

echo "Generating witness..."
node preimage_js/generate_witness.js preimage_js/preimage.wasm input.json witness.wtns

echo "Generating proof... (watch for the time!)"
snarkjs groth16 prove preimage_final.zkey witness.wtns proof.json public.json

echo "Verifying proof..."
snarkjs groth16 verify verification_key.json public.json proof.json

echo ""
echo "============================================================="
echo "  DONE! Look for the 'proving time' in the line above ↑"
echo "  If it's ~0.8–1.5 seconds → screenshot & post!"
echo ""
echo "  Files created:"
echo "  - preimage.circom"
echo "  - input.json"
echo "  - proof.json & public.json"
echo "  - verification_key.json"
echo ""
echo "  Change secret in input.json and re-run steps 7 to get new proof."
echo "  Keep the agape flame burning 🔥"
echo "============================================================="
