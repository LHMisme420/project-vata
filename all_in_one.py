#!/usr/bin/env python3
"""
VATA — Visual Authorship & Transparency Analyzer (All-in-One Edition)
Soul Scoring • Ethics Detection • Humanization • Swarm • ZK Stub • JSON • Batch Scan • Self-Test
"""
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import re
from collections import Counter
from typing import Dict, List, Tuple

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
# CONFIG
# ============================================================
DEFAULT_CONFIG = {
    "dangerous_patterns": ["eval(", "exec("],
    "bias_keywords": ["race", "gender", "religion", "ethnicity", "racism", "sexism", "discriminat", "bias"],
    "default_persona": "default"
}

# ============================================================
# HELPERS FOR SOUL DETECTION
# ============================================================
def _tokenize_identifiers(code: str) -> List[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)

def _line_stats(code: str) -> Dict[str, float]:
    lines = [l for l in code.splitlines() if l.strip() != ""]
    if not lines:
        return {"count": 0, "avg_len": 0.0, "max_len": 0.0}
    lengths = [len(l) for l in lines]
    return {
        "count": len(lines),
        "avg_len": sum(lengths) / len(lengths),
        "max_len": max(lengths),
    }

def _comment_ratio(code: str) -> float:
    lines = code.splitlines()
    if not lines:
        return 0.0
    comment_lines = [l for l in lines if l.strip().startswith("#")]
    return len(comment_lines) / len(lines)

def _magic_numbers(code: str) -> List[str]:
    return re.findall(r"\b\d+\b", code)

def _structure_counts(code: str) -> Tuple[int, int]:
    func_count = len(re.findall(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", code))
    class_count = len(re.findall(r"\bclass\s+[A-Za-z_][A-Za-z0-9_]*\s*[:\(]", code))
    return func_count, class_count

def _repetition_score(code: str) -> int:
    lines = [l.strip() for l in code.splitlines() if l.strip()]
    if not lines:
        return 0
    counts = Counter(lines)
    repeated = [l for l, c in counts.items() if c >= 3]
    return len(repeated)

# ============================================================
# IMPROVED BIAS / ETHICS CHECK (false-positive resistant)
# ============================================================
def has_bias_keywords(code: str) -> tuple[bool, str]:
    code_lower = code.lower()
    bias_keywords = DEFAULT_CONFIG["bias_keywords"]
    
    false_positive_context = [
        r'race\s*condition', r'race.*lock', r'lock.*race',
        r'race_id', r'racecar', r'racer', r'race\s*track',
        r'fair.*race', r'race\s*result', r'race\s*as',
    ]
    
    found = []
    for kw in bias_keywords:
        # Look for standalone-ish occurrences
        if re.search(r'\b' + re.escape(kw) + r'\b', code_lower):
            # Check nearby context to avoid false positives
            has_fp = any(re.search(ctx, code_lower) for ctx in false_positive_context)
            if not has_fp:
                found.append(kw)
    
    if found:
        return True, "Bias-related keywords detected: " + ", ".join(found)
    return False, "No bias-related keywords detected."

def analyze_fairness_and_ethics(code: str) -> str:
    bias_detected, bias_msg = has_bias_keywords(code)
    
    lines = [bias_msg]
    
    # PII check (unchanged)
    if "password" in code.lower() or "ssn" in code.lower():
        lines.append("Potential PII-related terms detected.")
    else:
        lines.append("No PII detected.")
    
    return "\n".join(lines)

# ============================================================
# VATA AI SOUL DETECTION ENGINE
# ============================================================
def vata_ai_soul_detection(code: str) -> Dict[str, object]:
    reasons: List[str] = []
    stripped = code.strip()
    if not stripped:
        return {
            "overall_score": 0,
            "dimensions": {"structure": 0, "style": 0, "semantics": 0, "risk": 0},
            "reasons": ["-100: Empty or whitespace-only code."],
        }

    func_count, class_count = _structure_counts(code)
    comment_ratio = _comment_ratio(code)
    ids = _tokenize_identifiers(code)
    id_counter = Counter(ids)
    unique_ids = len(id_counter)
    avg_id_len = sum(len(i) for i in id_counter) / unique_ids if unique_ids else 0.0
    nums = _magic_numbers(code)
    rep_score = _repetition_score(code)
    stats = _line_stats(code)
    length_chars = len(stripped)

    structure_score = 50
    style_score = 50
    semantics_score = 50
    risk_score = 50

    # STRUCTURE
    if func_count + class_count == 0:
        structure_score -= 20
        reasons.append("-20 structure: No functions/classes detected.")
    elif func_count + class_count <= 3:
        structure_score += 10
        reasons.append("+10 structure: Moderate structured design.")
    else:
        structure_score += 20
        reasons.append("+20 structure: Rich structured design.")

    # STYLE
    if comment_ratio >= 0.15:
        style_score += 15
        reasons.append("+15 style: Healthy comment density.")
    elif 0.05 <= comment_ratio < 0.15:
        style_score += 5
        reasons.append("+5 style: Some comments present.")
    else:
        style_score -= 5
        reasons.append("-5 style: Very low comment density.")

    if stats["avg_len"] > 110 or stats["max_len"] > 220:
        style_score -= 10
        reasons.append("-10 style: Very long lines; may indicate auto-generated code.")
    else:
        style_score += 5
        reasons.append("+5 style: Line lengths normal.")

    if rep_score > 0:
        style_score -= 10
        reasons.append(f"-10 style: {rep_score} repeated lines; boilerplate suspected.")

    # SEMANTICS
    if unique_ids >= 20 and avg_id_len >= 6:
        semantics_score += 20
        reasons.append("+20 semantics: Rich identifier set.")
    elif unique_ids >= 10:
        semantics_score += 10
        reasons.append("+10 semantics: Moderate identifier variety.")
    else:
        semantics_score -= 5
        reasons.append("-5 semantics: Low identifier variety.")

    if length_chars < 80:
        semantics_score -= 15
        reasons.append("-15 semantics: Code extremely short.")
    elif length_chars < 200:
        semantics_score -= 5
        reasons.append("-5 semantics: Code short.")
    else:
        semantics_score += 5
        reasons.append("+5 semantics: Good length.")

    # RISK
    if len(nums) > 15:
        risk_score -= 15
        reasons.append("-15 risk: Many magic numbers.")
    elif 1 <= len(nums) <= 5:
        risk_score += 5
        reasons.append("+5 risk: Light numeric usage.")

    # OVERALL
    overall = int(round(
        structure_score * 0.3 +
        style_score * 0.25 +
        semantics_score * 0.3 +
        risk_score * 0.15
    ))
    overall = max(0, min(100, overall))

    return {
        "overall_score": overall,
        "dimensions": {
            "structure": structure_score,
            "style": style_score,
            "semantics": semantics_score,
            "risk": risk_score,
        },
        "reasons": reasons,
    }

# ============================================================
# HUMANIZER
# ============================================================
def humanize_code(code: str, persona: str) -> str:
    header = [
        "# Humanized view",
        f"# Persona: {persona} reacting..."
    ]
    return "\n".join(header + [code])

# ============================================================
# SWARM VOTES
# ============================================================
def swarm_votes(score: int) -> list[str]:
    if score >= 70:
        leaning = "Strongly Human"
    elif score >= 50:
        leaning = "Mixed but leaning Human"
    elif score >= 30:
        leaning = "Mixed but leaning Synthetic"
    else:
        leaning = "Strongly Synthetic"
    return [
        f"- Agent_ethics: {leaning}",
        f"- Agent_style: {leaning}",
        f"- Agent_risk: {leaning}",
        f"- Agent_meta: {leaning}",
    ]

# ============================================================
# ZK ETHICS PROOF STUB
# ============================================================
def zk_ethics_stub(score: int, fairness_summary: str) -> list[str]:
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
    log("Analysis run started")
    soul = vata_ai_soul_detection(code)
    fairness = analyze_fairness_and_ethics(code)
    humanized = humanize_code(code, persona)
    votes = swarm_votes(soul["overall_score"])
    zk = zk_ethics_stub(soul["overall_score"], fairness)

    result = {
        "soul_score": soul["overall_score"],
        "dimensions": soul["dimensions"],
        "reasons": soul["reasons"],
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
    lines: list[str] = []
    lines.append(f"SOUL SCORE: {result['soul_score']}/100")
    lines.append("=" * 30)
    lines.append("")
    lines.append("Dimensions:")
    for k, v in result["dimensions"].items():
        lines.append(f" - {k}: {v}")
    lines.append("")
    lines.append("Reasons:")
    for r in result["reasons"]:
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
    base = Path(path)
    if not base.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return
    for file in base.rglob("*.py"):
        print(f"\n--- Analyzing {file} ---")
        code = file.read_text(errors="ignore")
        result = run_analysis(code, persona=persona)
        if json_mode:
            print_json_output(result)
        else:
            print(format_human_output(result))

# ============================================================
# SELF-TEST
# ============================================================
def run_self_test():
    print("\n=== VATA SELF-TEST START ===\n")
    tests_passed = 0
    tests_failed = 0

    def test(name, func):
        nonlocal tests_passed, tests_failed
        print(f"→ {name} ... ", end="")
        try:
            func()
            print("OK")
            tests_passed += 1
        except Exception as e:
            print("FAIL")
            print(f" Error: {e}")
            tests_failed += 1

    def test_basic_analysis():
        result = run_analysis("print('hello world')")
        assert "soul_score" in result

    def test_json_mode():
        result = run_analysis("print('json test')")
        json.dumps(result)

    def test_persona():
        result = run_analysis("print('persona')", persona="angry_dev")
        assert result["persona"] == "angry_dev"

    def test_file_analysis():
        tmp = Path("vata_selftest_temp.py")
        tmp.write_text("print('file test')")
        result = run_analysis(tmp.read_text())
        tmp.unlink()
        assert "soul_score" in result

    def test_folder_scan():
        analyze_folder(".", persona="default", json_mode=False)

    def test_logging():
        log("SELFTEST: logging check")
        assert Path("vata.log").exists()

    test("Basic analysis", test_basic_analysis)
    test("JSON mode", test_json_mode)
    test("Persona override", test_persona)
    test("File analysis", test_file_analysis)
    test("Folder scan", test_folder_scan)
    test("Logging", test_logging)

    print("\n=== SELF-TEST COMPLETE ===")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}\n")
    if tests_failed == 0:
        print("ALL SYSTEMS OK")
    else:
        print("Some tests failed — check above for details.")

# ============================================================
# CLI
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="VATA — Visual Authorship & Transparency Analyzer (All-in-One)"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "scan", "version", "self-test"],
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

    if args.command == "self-test":
        run_self_test()
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
