#!/usr/bin/env bash
set -e

CIRCUIT=$1
if [ -z "$CIRCUIT" ]; then
  echo "Usage: $0 <circuit_name>   (poseidon_preimage or merkle_inclusion)"
  exit 1
fi

mkdir -p ptau build

echo "→ Downloading powers-of-tau (16)..."
curl -L -o ptau/powersOfTau28_hez_final_16.ptau \
  https://hermez.s3-eu-west-1.amazonaws.com/powersOfTau28_hez_final_16.ptau

echo "→ Contributing Phase 1 (agape ritual)..."
snarkjs powersoftau contribute ptau/powersOfTau28_hez_final_16.ptau \
  ptau/${CIRCUIT}_contrib.ptau --name="agape-${CIRCUIT}-love-truth-uplift" -v

echo "→ Compiling circuit..."
circom circuits/${CIRCUIT}.circom --r1cs --wasm --sym -o build/

echo "→ Phase 2 setup..."
snarkjs zkey new build/${CIRCUIT}.r1cs ptau/${CIRCUIT}_contrib.ptau \
  ${CIRCUIT}_0000.zkey

echo "→ Contributing Phase 2..."
snarkjs zkey contribute ${CIRCUIT}_0000.zkey ${CIRCUIT}_final.zkey \
  --name="agape-phase2-$(date +%Y%m%d)" -v

echo "→ Export verification key..."
snarkjs zkey export verificationkey ${CIRCUIT}_final.zkey \
  ${CIRCUIT}_verification_key.json

echo "Done. Final zkey: ${CIRCUIT}_final.zkey"
echo "Next: create input.json and run snarkjs groth16 prove / fullProve"
