#!/usr/bin/env python3
"""
VATA — Visual Authorship & Transparency Analyzer (All-in-One Edition)
Soul Scoring • Ethics Detection • Humanization • Swarm • ZK Stub • JSON • Batch Scan
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

# ============================================================
# VERSION
# ============================================================

VERSION = "1.0.0"


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="vata.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(msg: str) -> None:
    logging.info(msg)


# ============================================================
# CONFIG (INLINE DEFAULTS, CAN BE EXTERNALIZED LATER)
# ============================================================

DEFAULT_CONFIG = {
    "dangerous_patterns": ["eval(", "exec("],
    "bias_keywords": ["race", "gender", "religion", "ethnicity"],
    "default_persona": "default"
}


# ============================================================
# CORE SOUL SCORING ENGINE
# ============================================================

def compute_soul_score(code: str) -> tuple[int, list[str]]:
    """
    Very simple heuristic scoring:
    - Comments
    - Identifiers
    - Dangerous patterns
    - Length
    """
    score = 50
    reasons: list[str] = []

    # Comments
    if "#" in code:
        score += 10
        reasons.append("+10: Comments detected.")
    else:
        reasons.append("0: No comments detected.")

    # Identifiers
    meaningful_identifiers = 0
    for token in ["user", "client", "order", "session", "config"]:
        if token in code:
            meaningful_identifiers += 1
    if meaningful_identifiers > 0:
        score += 20
        reasons.append("+20: Found meaningful identifiers.")
    else:
        reasons.append("0: No meaningful identifiers found.")

    # Dangerous patterns
    dangerous_hits = 0
    for pattern in DEFAULT_CONFIG["dangerous_patterns"]:
        if pattern in code:
            dangerous_hits += 1
    if dangerous_hits > 0:
        penalty = 20 * dangerous_hits
        score -= penalty
        reasons.append(f"-{penalty}: Dangerous patterns detected ({dangerous_hits} hits).")
    else:
        reasons.append("0: No dangerous patterns detected.")

    # Length
    if len(code.strip()) < 20:
        score -= 10
        reasons.append("-10: Code is very short/trivial.")
    else:
        reasons.append("0: Code length is reasonable.")

    # Clamp
    score = max(0, min(100, score))
    return score, reasons


# ============================================================
# FAIRNESS / ETHICS SCAN
# ============================================================

def analyze_fairness_and_ethics(code: str) -> str:
    """
    Simple keyword-based fairness/ethics scan.
    """
    lines: list[str] = []
    bias_hits = []

    for kw in DEFAULT_CONFIG["bias_keywords"]:
        if kw.lower() in code.lower():
            bias_hits.append(kw)

    if bias_hits:
        lines.append("Bias-related keywords detected: " + ", ".join(bias_hits))
    else:
        lines.append("No bias-related keywords detected.")

    # PII heuristic
    if "password" in code.lower() or "ssn" in code.lower():
        lines.append("Potential PII-related terms detected.")
    else:
        lines.append("No PII detected.")

    return "\n".join(lines)


# ============================================================
# HUMANIZER
# ============================================================

def humanize_code(code: str, persona: str) -> str:
    """
    Wrap code with persona-based commentary.
    """
    header = [
        "# Humanized view",
        f"# Persona: {persona} reacting..."
    ]
    return "\n".join(header + [code])


# ============================================================
# SWARM VOTES
# ============================================================

def swarm_votes(score: int) -> list[str]:
    """
    Simple synthetic swarm interpretation of the score.
    """
    if score >= 70:
        leaning = "Strongly Human"
    elif score >= 50:
        leaning = "Mixed but leaning Human"
    elif score >= 30:
        leaning = "Mixed but leaning Synthetic"
    else:
        leaning = "Strongly Synthetic"

    votes = [
        f"- Agent_ethics: {leaning}",
        f"- Agent_style: {leaning}",
        f"- Agent_risk: {leaning}",
        f"- Agent_meta: {leaning}",
    ]
    return votes


# ============================================================
# ZK ETHICS PROOF STUB
# ============================================================

def zk_ethics_stub(score: int, fairness_summary: str) -> list[str]:
    """
    Stub for future ZK-proof integration.
    """
    fairness_hash = f"<hash({fairness_summary[:40]}...)>"
    proof_bytes = "<placeholder>"

    return [
        f'- Statement: "Soul score = {score}/100 under VATA-Ethics-v1."',
        f"- Fairness summary hash: {fairness_hash}",
        f"- Proof bytes: {proof_bytes}",
    ]


# ============================================================
# CORE ANALYSIS PIPELINE
# ============================================================

def run_analysis(code: str, persona: str = "default") -> dict:
    """
    Run the full VATA pipeline on a code string.
    Returns a dict with all components.
    """
    log("Analysis run started")

    score, reasons = compute_soul_score(code)
    fairness = analyze_fairness_and_ethics(code)
    humanized = humanize_code(code, persona)
    votes = swarm_votes(score)
    zk = zk_ethics_stub(score, fairness)

    result = {
        "soul_score": score,
        "breakdown": reasons,
        "fairness_ethics": fairness.split("\n"),
        "humanized": humanized.split("\n"),
        "swarm_votes": votes,
        "zk_proof": zk,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": VERSION,
        "persona": persona,
    }

    log("Analysis run completed")
    return result


# ============================================================
# OUTPUT HELPERS
# ============================================================

def format_human_output(result: dict) -> str:
    """
    Render a human-readable multi-section output.
    """
    lines: list[str] = []
    lines.append(f"SOUL SCORE: {result['soul_score']}/100")
    lines.append("=" * 30)
    lines.append("")
    lines.append("Breakdown:")
    for r in result["breakdown"]:
        lines.append(f" - {r}")
    lines.append("")
    lines.append("Fairness / Ethics:")
    for line in result["fairness_ethics"]:
        lines.append(line)
    lines.append("")
    lines.append("Humanized Version:")
    for line in result["humanized"]:
        lines.append(line)
    lines.append("")
    lines.append("Swarm Votes:")
    for v in result["swarm_votes"]:
        lines.append(v)
    lines.append("")
    lines.append("ZK Proof Stub:")
    for z in result["zk_proof"]:
        lines.append(z)
    lines.append("")
    lines.append(f"Version: {result['version']}")
    lines.append(f"Persona: {result['persona']}")
    lines.append(f"Timestamp: {result['timestamp']}")
    return "\n".join(lines)


def print_json_output(result: dict) -> None:
    print(json.dumps(result, indent=2))


# ============================================================
# BATCH FOLDER SCAN
# ============================================================

def analyze_folder(path: str, persona: str = "default", json_mode: bool = False) -> None:
    """
    Walk a folder, analyze all .py files.
    """
    base = Path(path)
    if not base.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return

    all_results = {}

    for file in base.rglob("*.py"):
        try:
            code = file.read_text(errors="ignore")
        except Exception as e:
            print(f"[WARN] Could not read {file}: {e}")
            continue

        print(f"\n--- Analyzing {file} ---")
        result = run_analysis(code, persona=persona)
        all_results[str(file)] = result

        if json_mode:
            print_json_output(result)
        else:
            print(format_human_output(result))

    if json_mode:
        # If you want a single JSON blob for the whole folder, you could:
        # print(json.dumps(all_results, indent=2))
        pass


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VATA — Visual Authorship & Transparency Analyzer (All-in-One)"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "scan", "version"],
        help="Command to run"
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="File path, folder path, or dummy placeholder when using --text"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Analyze raw code passed as a string instead of a file"
    )
    parser.add_argument(
        "--persona",
        type=str,
        default=DEFAULT_CONFIG["default_persona"],
        help="Persona to use for humanization"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    if args.command == "version":
        print(f"VATA Version: {VERSION}")
        return

    if args.command == "analyze":
        if args.text:
            code = args.text
        else:
            if not args.target:
                print("[ERROR] You must provide a file path or use --text.")
                return
            path = Path(args.target)
            if not path.exists():
                print(f"[ERROR] File not found: {path}")
                return
            code = path.read_text(errors="ignore")

        result = run_analysis(code, persona=args.persona)
        if args.json:
            print_json_output(result)
        else:
            print(format_human_output(result))

    elif args.command == "scan":
        if not args.target:
            print("[ERROR] You must provide a folder path for scan.")
            return
        analyze_folder(args.target, persona=args.persona, json_mode=args.json)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
