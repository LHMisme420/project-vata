const fs = require('fs');
const snarkjs = require('snarkjs');

async function main() {
  try {
    const publicSignals = JSON.parse(fs.readFileSync('public.json', 'utf8'));
    const proof = JSON.parse(fs.readFileSync('proof.json', 'utf8'));
    const calldata = await snarkjs.groth16.exportSolidityCallData(proof, publicSignals);
    console.log(calldata);
  } catch (e) {
    console.error('Error:', e.message);
  }
}

main();