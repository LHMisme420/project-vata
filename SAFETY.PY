import ast
import os
import hashlib

def get_logic_fingerprint(directory: str = ".") -> dict:
    """
    Extract a basic 'logic fingerprint' from Python files in a directory.
    Counts AST nodes and flags complex constructs (comprehensions, with, lambda).
    """
    stats = {"nodes": 0, "complexity": 0, "patterns": []}
    
    for root, _, files in os.walk(directory):
        for f_name in files:
            if f_name.endswith(".py") and "vata" not in f_name.lower():
                file_path = os.path.join(root, f_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            stats["nodes"] += 1
                            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp,
                                                 ast.GeneratorExp, ast.With, ast.Lambda)):
                                stats["complexity"] += 2
                        stats["patterns"].append(f"{f_name}:{stats['nodes']}")
                    except SyntaxError:
                        continue
    return stats

def apply_safety_seal(code_string: str) -> str:
    """Generate a simple hash-based seal for code (expand with entropy checks later)."""
    fingerprint = hashlib.sha256(code_string.encode("utf-8")).hexdigest()
    return fingerprint

def verify_fingerprint(code_string: str, expected_seal: str) -> bool:
    """Basic verification: recompute seal and compare."""
    return apply_safety_seal(code_string) == expected_seal

# Example usage (for testing)
if __name__ == "__main__":
    sample_code = "def hello(): return [x for x in range(10)]"
    seal = apply_safety_seal(sample_code)
    print(f"Seal: {seal}")
    print(f"Verified: {verify_fingerprint(sample_code, seal)}")
