import ast
import os
import hashlib
from typing import Dict

def get_logic_fingerprint(directory: str = ".") -> Dict:
    """
    Scans Python files in the directory (excluding vata itself) and builds a simple logic fingerprint
    based on AST nodes and complexity patterns – humans tend to have more "quirky" structures.
    """
    stats = {"nodes": 0, "complexity": 0, "patterns": []}
    
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py") and "vata" not in file_name.lower():
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source)
                    
                    for node in ast.walk(tree):
                        stats["nodes"] += 1
                        if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp,
                                             ast.GeneratorExp, ast.With, ast.AsyncWith, ast.Lambda)):
                            stats["complexity"] += 2
                    
                    stats["patterns"].append(f"{file_name}: nodes={stats['nodes']}, complexity={stats['complexity']}")
                except Exception:
                    # Skip files with syntax errors
                    continue
    
    # Add a hash of the stats for sealing
    stats["hash"] = hashlib.sha256(str(stats).encode("utf-8")).hexdigest()
    return stats

def apply_safety_seal(code_string: str) -> str:
    """Creates a cryptographic seal (SHA-256 hash) for a piece of code."""
    return hashlib.sha256(code_string.strip().encode("utf-8")).hexdigest()

def verify_fingerprint(code_string: str, expected_seal: str) -> bool:
    """Verifies if the code matches the previously created seal."""
    return apply_safety_seal(code_string) == expected_seal
