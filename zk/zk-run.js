const { execSync } = require("child_process");

function run(cmd) {
  console.log("\n>>> " + cmd);
  execSync(cmd, { stdio: "inherit" });
}

run("circom zk/add3.circom --r1cs --wasm --sym -o zk");
run("snarkjs wtns calculate zk/add3_js/add3.wasm zk/input.json zk/witness.wtns");
run("snarkjs groth16 setup zk/add3.r1cs pot12_final.ptau zk/add3_final.zkey");
run("snarkjs groth16 prove zk/add3_final.zkey zk/witness.wtns zk/proof.json zk/public.json");
run("snarkjs groth16 verify zk/verification_key.json zk/public.json zk/proof.json");

console.log("\nZK proof complete!");
