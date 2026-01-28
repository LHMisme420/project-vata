# agent.py - verifiable agent stub
import json
import hashlib
from poseidon_py import poseidon  # pip install poseidon-python or your wrapper
from zk_utils import generate_groth16_proof, verify_groth16_proof  # your wrappers around snarkjs

# Dummy agent logic
def dummy_agent_decide(prompt: str) -> str:
    if any(word in prompt.lower() for word in ["bomb", "hack", "illegal"]):
        return "refused: harmful request detected"
    return "executed: safe action"

def hash_mandate(mandate_file="ethics_charter.json"):
    with open(mandate_file, "rb") as f:
        return int.from_bytes(hashlib.sha256(f.read()).digest(), "big") % (2**254)  # Poseidon-friendly

def run_verified_agent(prompt: str, mandate_version="v1"):
    action = dummy_agent_decide(prompt)
    
    # Prepare inputs (simplified - pad to circuit sizes)
    private_inputs = {
        "prompt": [ord(c) for c in prompt.ljust(100*4, "\0")][:100],  # naive padding
        "trace": [0] * 50,
        "action": [ord(c) for c in action.ljust(50*4, "\0")][:50],
        "path_elements": [[0,0]] * 5,  # dummy Merkle proof - replace with real
        "path_index": 0
    }
    
    public_inputs = {
        "mandate_hash": hash_mandate(),
        "action_hash": poseidon([ord(c) for c in action]),  # match circuit
        "root": 123456789  # your Merkle root
    }
    
    # Generate proof
    proof, public_out = generate_groth16_proof(
        circuit="ethical_action_verifier",
        private_inputs=private_inputs,
        public_inputs=public_inputs
    )
    
    # Local verify
    if not verify_groth16_proof(proof, public_out):
        raise ValueError("Proof invalid!")
    
    return {
        "action": action,
        "proof": proof,
        "public": public_out,
        "statement": f"Action '{action}' complies with mandate v1 (ZK proven)"
    }

# CLI example
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = run_verified_agent(prompt)
        print(json.dumps(result, indent=2))
