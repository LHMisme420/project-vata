from vata.safety import apply_safety_seal, verify_fingerprint

code_seal = apply_safety_seal(your_code_string)
is_human = verify_fingerprint(code_seal)
import ast, os, hashlib

def get_logic_fingerprint(directory="."):
    stats = {"nodes": 0, "complexity": 0, "patterns": ""}
    for root, _, files in os.walk(directory):
        for f_name in files:
            if f_name.endswith(".py") and "vata" not in f_name:
                with open(os.path.join(root, f_name), "r") as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            stats["nodes"] += 1
                            if isinstance(node, (ast.ListComp, ast.With, ast.Lambda)):
                                stats["complexity"] += 2
                        stats["patterns"] += f_name + str(stats["nodes"])
                    except: continue
    return stats
