#!/usr/bin/env python3
"""
VATA Simple – Soul Score for Python Code
"""

import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple

def analyze_code(code: str) -> Dict:
    """Core soul detection – simple version"""
    code = code.strip()
    if not code:
        return {
            "soul_score": 0,
            "verdict": "EMPTY",
            "dimensions": {"structure": 0, "style": 0, "semantics": 0, "risk": 0},
            "reasons": ["Empty code"]
        }

    # Helpers
    lines = [l for l in code.splitlines() if l.strip()]
    length_chars = len(code)
    comment_ratio = sum(1 for l in lines if l.strip().startswith("#")) / max(1, len(lines))
    ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)
    unique_ids = len(set(ids))
    magic_nums = len(re.findall(r"\b\d+\b", code))
    funcs = len(re.findall(r"\bdef\s+\w+", code))
    classes = len(re.findall(r"\bclass\s+\w+", code))
    repeated_lines = len([l for l, c in Counter(lines).items() if c >= 3])

    # Scores start at 50
    structure = 50
    style     = 50
    semantics = 50
    risk      = 50
    reasons   = []

    # Structure
    total_struct = funcs + classes
    if total_struct == 0:
        structure -= 20
        reasons.append("-20 No functions or classes")
    elif total_struct <= 3:
        structure += 5
        reasons.append("+5 Some structure")
    else:
        structure += 15
        reasons.append("+15 Good structure")

    # Style
    if comment_ratio >= 0.12:
        style += 12
        reasons.append("+12 Decent comments")
    elif comment_ratio >= 0.03:
        style += 4
        reasons.append("+4 Some comments")
    else:
        style -= 8
        reasons.append("-8 Almost no comments")

    if repeated_lines > 0:
        style -= 10
        reasons.append(f"-10 Repeated lines ({repeated_lines})")

    # Semantics
    if unique_ids >= 15:
        semantics += 15
        reasons.append("+15 Good identifier variety")
    elif unique_ids >= 5:
        semantics += 5
        reasons.append("+5 Some variety")
    else:
        semantics -= 10
        reasons.append("-10 Very few unique names")

    if length_chars < 100:
        semantics -= 15
        reasons.append("-15 Very short code")
    elif length_chars > 300:
        semantics += 5
        reasons.append("+5 Solid length")

    # Risk
    if magic_nums > 12:
        risk -= 12
        reasons.append("-12 Too many magic numbers")
    elif magic_nums <= 4:
        risk += 6
        reasons.append("+6 Light number usage")

    # Final soul score
    soul = int(round(
        structure * 0.35 +
        style     * 0.25 +
        semantics * 0.25 +
        risk      * 0.15
    ))
    soul = max(0, min(100, soul))

    verdict = "HUMAN" if soul >= 70 else "MIXED" if soul >= 40 else "AI"

    # Simple ethics check (with race-condition protection)
    bias_words = ["race", "gender", "ethnicity", "racism", "sexism"]
    bias_found = []
    for word in bias_words:
        if re.search(r'\b' + word + r'\b', code.lower()):
            if not re.search(r'race\s*condition|race_id|racecar|racer', code.lower()):
                bias_found.append(word)

    ethics = "Bias keywords: " + ", ".join(bias_found) if bias_found else "No bias keywords"

    return {
        "soul_score": soul,
        "verdict": verdict,
        "dimensions": {
            "structure": structure,
            "style": style,
            "semantics": semantics,
            "risk": risk
        },
        "reasons": reasons,
        "ethics": ethics
    }


def scan_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Error: {folder} is not a folder")
        return

    print(f"\nScanning: {folder}")
    print("-" * 50)

    for file in folder.rglob("*.py"):
        try:
            code = file.read_text(encoding="utf-8", errors="ignore")
            result = analyze_code(code)

            print(f"\n{file.name}")
            print(f"  Soul: {result['soul_score']}/100  →  {result['verdict']}")
            print(f"  Ethics: {result['ethics']}")
            if result['reasons']:
                print("  Reasons:")
                for r in result['reasons'][:5]:  # limit to top 5
                    print(f"    {r}")
            print("  Dimensions:", " | ".join(f"{k}:{v}" for k,v in result['dimensions'].items()))

        except Exception as e:
            print(f"  Error reading {file.name}: {e}")

    print("\nScan complete.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python vata_simple.py /path/to/folder")
        sys.exit(1)

    scan_folder(sys.argv[1])
