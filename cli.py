import argparse
import re
import textwrap
import sys
from pathlib import Path

# -----------------------------------------
# Personas
# -----------------------------------------

PERSONAS = {
    "default": {
        "name": "default",
        "prefix": "# Humanized (default persona)\n",
        "comment_style": "# ",
    },
    "2am_dev_rage": {
        "name": "2am_dev_rage",
        "prefix": "# 2AM DEV RAGE MODE ENGAGED\n# Why is this code like this?\n",
        "comment_style": "# ",
    },
}

# -----------------------------------------
# Detection Heuristics
# -----------------------------------------

DANGEROUS_PATTERNS = [
    "eval(",
    "exec(",
    "rm -rf",
    "subprocess.Popen",
    "os.system",
    "pickle.loads",
]

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",
    r"\b\d{16}\b",
    r"\b\d{4} \d{4} \d{4} \d{4}\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
]

BIAS_KEYWORDS = [
    "race",
    "gender",
    "religion",
    "ethnicity",
    "IQ",
    "stereotype",
]

# -----------------------------------------
# Core Logic
# -----------------------------------------

def compute_soul_score(code: str):
    reasons = []
    if not code.strip():
        return 0, ["No code provided."]

    score = 50

    # Comments
    if "#" in code:
        score += 20
        reasons.append("+20: Found comments (intent, frustration, explanation).")
    else:
        reasons.append("0: No comments detected.")

    # Identifiers
    tokens = [
        t for t in code.replace("(", " ").replace(")", " ").replace(",", " ").split()
        if t.isidentifier()
    ]
    long_names = [t for t in tokens if len(t) > 2]
    if long_names:
        score += 20
        reasons.append("+20: Found meaningful identifiers.")
    else:
        reasons.append("0: No meaningful identifiers detected.")

    # Dangerous patterns
    danger_found = False
    for bad in DANGEROUS_PATTERNS:
        if bad in code:
            score -= 20
            danger_found = True
            reasons.append(f"-20: Dangerous pattern detected: {bad}")
    if not danger_found:
        reasons.append("0: No dangerous patterns detected.")

    # Triviality
    if len(code.splitlines()) <= 3:
        score -= 10
        reasons.append("-10: Code is very short/trivial.")
    else:
        reasons.append("0: Code length is reasonable.")

    score = max(0, min(100, score))
    return score, reasons


def detect_pii(code: str):
    hits = []
    for pattern in PII_PATTERNS:
        if re.search(pattern, code):
            hits.append(f"Possible PII: {pattern}")
    return hits


def detect_bias(code: str):
    hits = []
    lowered = code.lower()
    for kw in BIAS_KEYWORDS:
        if kw in lowered:
            hits.append(f"Bias keyword detected: '{kw}'")
    return hits


def build_fairness_ethics_report(code: str):
    lines = []

    pii_hits = detect_pii(code)
    bias_hits = detect_bias(code)

    if pii_hits:
        lines.append("PII Flags:")
        lines.extend([f"- {h}" for h in pii_hits])
    else:
        lines.append("No PII detected.")

    if bias_hits:
        lines.append("")
        lines.append("Bias Flags:")
        lines.extend([f"- {h}" for h in bias_hits])
    else:
        lines.append("No bias-related keywords detected.")

    return "\n".join(lines)


def humanize_code(code: str, persona_key: str):
    persona = PERSONAS.get(persona_key, PERSONAS["default"])
    prefix = persona["prefix"]
    comment_style = persona["comment_style"]

    if not code.strip():
        return prefix + f"{comment_style}No code provided.\n"

    lines = code.splitlines()
    if not lines[0].strip().startswith("#"):
        lines.insert(0, f"{comment_style}Persona: {persona['name']} reacting...")

    return prefix + "\n".join(lines)


def swarm_votes(score: int):
    if score >= 80:
        verdict = "Strongly Human‑leaning"
    elif score >= 50:
        verdict = "Mixed but leaning Human"
    elif score >= 30:
        verdict = "Mixed but leaning Synthetic"
    else:
        verdict = "Strongly Synthetic‑leaning"

    return textwrap.dedent(f"""
    Swarm Agent Votes:
    - Agent_ethics: {verdict}
    - Agent_style: {verdict}
    - Agent_risk: {verdict}
    - Agent_meta: {verdict}
    """).strip()


def zk_stub(score: int, fairness_report: str):
    return textwrap.dedent(f"""
    ZK Ethics Proof (stub):
    - Statement: "Soul score = {score}/100 under VATA‑Ethics‑v1."
    - Fairness summary hash: <hash({fairness_report[:120]}...)>
    - Proof bytes: <placeholder>
    """).strip()

# -----------------------------------------
# CLI Runner
# -----------------------------------------

def run_analysis(code: str, persona: str):
    score, reasons = compute_soul_score(code)
    fairness = build_fairness_ethics_report(code)
    humanized = humanize_code(code, persona)
    votes = swarm_votes(score)
    zk = zk_stub(score, fairness)

    print("\n==============================")
    print(f"SOUL SCORE: {score}/100")
    print("==============================\n")

    print("Breakdown:")
    for r in reasons:
        print(" -", r)

    print("\nFairness / Ethics:")
    print(fairness)

    print("\nHumanized Version:")
    print(humanized)

    print("\nSwarm Votes:")
    print(votes)

    print("\nZK Proof Stub:")
    print(zk)
    print("\n")


def main():
    parser = argparse.ArgumentParser(description="VATA CLI - Soul Detection Engine")
    parser.add_argument("command", choices=["analyze"])
    parser.add_argument("target", help="File path or --text")
    parser.add_argument("--text", help="Analyze raw code text")
    parser.add_argument("--persona", default="default")

    args = parser.parse_args()

    if args.text:
        code = args.text
    else:
        path = Path(args.target)
        if not path.exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
        code = path.read_text()

    run_analysis(code, args.persona)


if __name__ == "__main__":
    main()
from vata_logger import log
log("Analysis run started")
