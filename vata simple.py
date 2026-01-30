# vata_simple.py ── Single-file version of Project VATA (simplified)
# Just run: python vata_simple.py your_code.py
#         or python vata_simple.py   (tests itself)

import re
import sys
import math
import random
from pathlib import Path

# ── Very lightweight – no sentence-transformers / torch needed for this version ──

def simple_entropy(s):
    if not s: return 0
    counts = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    probs = [count / len(s) for count in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def score_soul(code):
    lines = [line for line in code.splitlines() if line.strip()]
    n_lines = max(1, len(lines))

    # Quick signals
    comment_count = len(re.findall(r'#|//|/\*|\* ', code))
    todo_count    = len(re.findall(r'(?i)TODO|FIXME|HACK|NOTE', code))
    debug_count   = len(re.findall(r'(?i)print\s*\(|console\.log|dbg|debug', code))
    quirky_count  = len(re.findall(r'(?i)\b(lol|wtf|shit|crap|pls|pain|rip|send help)\b', code))

    var_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', code)
    name_entropy = sum(simple_entropy(v) for v in var_names) / max(1, len(var_names)) if var_names else 0

    # Very simple score (0–100)
    score = 0
    score += min(30, comment_count * 2)
    score += min(20, (todo_count + debug_count + quirky_count) * 5)
    score += min(25, name_entropy * 8)
    score += min(25, min(1, n_lines / 15) * 25)   # longer code gets bonus if it has personality

    score = int(min(100, max(0, score)))

    category = "Trusted Artisan 🔥" if score >= 75 else "Suspicious 👻" if score <= 40 else "Mixed ⚖️"

    risks = []
    if re.search(r'(?i)api_key|secret|token|password', code): risks.append("Possible secret")
    if re.search(r'(?i)eval\(|exec\(', code): risks.append("Dangerous eval/exec")

    return {
        "soul_score": score,
        "category": category,
        "signals": {
            "comments": comment_count,
            "todo_debug_quirky": todo_count + debug_count + quirky_count,
            "name_entropy_avg": round(name_entropy, 2),
            "line_count": n_lines
        },
        "risks": risks
    }

def add_simple_soul(code):
    lines = code.splitlines()
    injections = [
        "# TODO: fix later lol",
        "# 3am vibes don't judge",
        "# send help this works somehow",
        "# debug – remove before commit",
        "# cursed but cute 💀",
    ]
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if random.random() < 0.18 and line.strip() and not line.strip().startswith('#'):
            new_lines.append("    " + random.choice(injections))
    return "\n".join(new_lines)

# ── Command line interface ──
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ["--help", "-h"]:
        print("Usage:")
        print("  python vata_simple.py your_code.py          → analyze file")
        print("  python vata_simple.py                       → analyze this file itself")
        print("  python vata_simple.py --humanize your_code.py → analyze + add soul")
        sys.exit(0)

    humanize = "--humanize" in sys.argv
    if humanize:
        sys.argv.remove("--humanize")

    if len(sys.argv) == 1:
        # self-test
        file_path = Path(__file__)
    else:
        file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    code = file_path.read_text(encoding="utf-8", errors="ignore")

    result = score_soul(code)

    print("\n" + "="*50)
    print(f"🛡️ VATA SIMPLE – {file_path.name}")
    print(f"Soul score: {result['soul_score']}/100  →  {result['category']}")
    print("Signals:", result["signals"])
    if result["risks"]:
        print("🚨 Risks:", ", ".join(result["risks"]))
    print("="*50 + "\n")

    if humanize:
        humanized = add_simple_soul(code)
        print("Humanized version:\n")
        print(humanized)
        print("\n" + "-"*50)
