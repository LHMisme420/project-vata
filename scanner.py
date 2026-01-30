# VATA Batch Scanner – Single-file, production-ready (no placeholders)
# =============================================================
# Instructions:
# 1. Replace ONLY the body of run_vata_analysis() below with your real detection code
# 2. Make sure it returns a dict with at least:
#       'ai_probability': float (0.0–1.0)
#       'verdict': str       ("HUMAN", "AI", "MIXED", "UNKNOWN", etc.)
#    Optional: 'soul_score', 'confidence', etc.
# 3. Change the target path at the bottom
# 4. Run: python this_file.py

import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from pathlib import Path

import re
from collections import Counter

def _tokenize_identifiers(code: str) -> list[str]:
    # crude but effective: grab words that look like identifiers
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)

def _line_stats(code: str) -> dict:
    lines = [l for l in code.splitlines() if l.strip() != ""]
    if not lines:
        return {
            "count": 0,
            "avg_len": 0,
            "max_len": 0,
        }
    lengths = [len(l) for l in lines]
    return {
        "count": len(lines),
        "avg_len": sum(lengths) / len(lengths),
        "max_len": max(lengths),
    }

def compute_soul_score(code: str) -> tuple[int, list[str]]:
    """
    Heuristic VATA-style detector:
    - structure (functions/classes)
    - identifier richness
    - comment density
    - magic numbers
    - repetition / boilerplate feel
    - AI-ish formatting patterns
    """
    score = 50
    reasons: list[str] = []

    stripped = code.strip()
    if not stripped:
        return 0, ["-50: Empty or whitespace-only code."]

    # --- Structure: functions / classes ---
    func_count = len(re.findall(r"\bdef\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", code))
    class_count = len(re.findall(r"\bclass\s+[A-Za-z_][A-Za-z0-9_]*\s*[:\(]", code))
    if func_count + class_count > 0:
        bump = 10 + 5 * min(func_count + class_count, 3)
        score += bump
        reasons.append(f"+{bump}: Structured code (functions/classes) detected.")
    else:
        reasons.append("0: No functions or classes detected.")

    # --- Comments & docstrings ---
    lines = code.splitlines()
    comment_lines = [l for l in lines if l.strip().startswith("#")]
    comment_ratio = (len(comment_lines) / len(lines)) if lines else 0.0

    if comment_ratio >= 0.15:
        score += 10
        reasons.append("+10: Healthy comment density.")
    elif 0.05 <= comment_ratio < 0.15:
        score += 5
        reasons.append("+5: Some comments present.")
    else:
        reasons.append("0: Low or no comments detected.")

    # --- Identifiers richness ---
    identifiers = _tokenize_identifiers(code)
    id_counter = Counter(identifiers)
    unique_ids = len(id_counter)
    avg_id_len = sum(len(i) for i in id_counter) / unique_ids if unique_ids else 0

    if unique_ids >= 15 and avg_id_len >= 6:
        score += 15
        reasons.append("+15: Rich, descriptive identifier set.")
    elif unique_ids >= 8:
        score += 8
        reasons.append("+8: Moderate identifier variety.")
    else:
        reasons.append("0: Low identifier variety (could be trivial or generated).")

    # --- Magic numbers / literals ---
    magic_numbers = re.findall(r"\b\d+\b", code)
    if len(magic_numbers) > 10:
        score -= 10
        reasons.append("-10: Many magic numbers; smells like low-level or generated code.")
    elif 1 <= len(magic_numbers) <= 3:
        score += 3
        reasons.append("+3: Light use of numeric literals (often human).")
    else:
        reasons.append("0: Neutral numeric literal usage.")

    # --- Repetition / boilerplate feel ---
    normalized_lines = [l.strip() for l in lines if l.strip()]
    line_counts = Counter(normalized_lines)
    repeated_lines = [l for l, c in line_counts.items() if c >= 3]

    if repeated_lines:
        score -= 10
        reasons.append("-10: Repeated identical lines; boilerplate/generation suspected.")
    else:
        reasons.append("0: No heavy repetition detected.")

    # --- AI-ish formatting patterns ---
    stats = _line_stats(code)
    if stats["avg_len"] > 100 or stats["max_len"] > 200:
        score -= 10
        reasons.append("-10: Very long lines; may indicate auto-generated or unreviewed code.")
    else:
        reasons.append("0: Line lengths within normal range.")

    # --- Length / triviality ---
    if len(stripped) < 40:
        score -= 15
        reasons.append("-15: Code is extremely short/trivial.")
    elif len(stripped) < 120:
        score -= 5
        reasons.append("-5: Code is quite short; limited signal.")
    else:
        score += 5
        reasons.append("+5: Sufficient code length for meaningful signal.")

    # Clamp
    score = max(0, min(100, score))
    return score, reasons
def run_vata_analysis(filepath: str) -> dict:
    """
    YOUR COMPLETE VATA AI/SOUL DETECTION FUNCTION
    
    - Read the file at 'filepath'
    - Run your full analysis (heuristics, model inference, soul markers, etc.)
    - Return this exact dict structure (add more keys if needed)
    """
   import re
from collections import Counter
from typing import Dict, List, Tuple

# ---------------------------------------------
# Helpers
# ---------------------------------------------

def _tokenize_identifiers(code: str) -> List[str]:
    # crude but effective: grab words that look like identifiers
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

# ---------------------------------------------
# Core VATA AI Soul Detection
# ---------------------------------------------

def vata_ai_soul_detection(code: str) -> Dict[str, object]:
    """
    VATA AI Soul Detection:
    Returns:
      - overall_score (0–100)
      - dimensions: structure/style/semantics/risk
      - reasons: list of human-readable explanations
    """
    reasons: List[str] = []
    stripped = code.strip()

    if not stripped:
        return {
            "overall_score": 0,
            "dimensions": {
                "structure": 0,
                "style": 0,
                "semantics": 0,
                "risk": 0,
            },
            "reasons": ["-100: Empty or whitespace-only code."],
        }

    # ---- Signals ----
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

    # ---- Dimension scores (0–100 each) ----
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
        reasons.append("+10 structure: Moderate structured design (functions/classes).")
    else:
        structure_score += 20
        reasons.append("+20 structure: Rich structured design (multiple functions/classes).")

    # STYLE (comments, line lengths, repetition)
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
        reasons.append("-10 style: Very long lines; may indicate auto-generated or unreviewed code.")
    else:
        style_score += 5
        reasons.append("+5 style: Line lengths within a human-typical range.")

    if rep_score > 0:
        style_score -= 10
        reasons.append(f"-10 style: {rep_score} heavily repeated lines; boilerplate/generation suspected.")
    else:
        reasons.append("0 style: No heavy repetition detected.")

    # SEMANTICS (identifiers, length, variety)
    if unique_ids >= 20 and avg_id_len >= 6:
        semantics_score += 20
        reasons.append("+20 semantics: Rich, descriptive identifier set.")
    elif unique_ids >= 10:
        semantics_score += 10
        reasons.append("+10 semantics: Moderate identifier variety.")
    else:
        semantics_score -= 5
        reasons.append("-5 semantics: Low identifier variety; could be trivial or generated.")

    if length_chars < 80:
        semantics_score -= 15
        reasons.append("-15 semantics: Code is extremely short; low semantic signal.")
    elif length_chars < 200:
        semantics_score -= 5
        reasons.append("-5 semantics: Code is short; limited semantic depth.")
    else:
        semantics_score += 5
        reasons.append("+5 semantics: Sufficient length for meaningful semantic signal.")

    # RISK (magic numbers, patterns, density)
    if len(nums) > 15:
        risk_score -= 15
        reasons.append("-15 risk: Many magic numbers; smells like low-level or generated code.")
    elif 1 <= len(nums) <= 5:
        risk_score += 5
        reasons.append("+5 risk: Light numeric usage; often human-tuned.")
    else:
        reasons.append("0 risk: Neutral numeric usage.")

    # You can plug in your dangerous patterns list here if you want:
    # for pattern in DEFAULT_CONFIG["dangerous_patterns"]:
    #     if pattern in code:
    #         risk_score -= 20
    #         reasons.append(f"-20 risk: Dangerous pattern detected: {pattern}")

    # ---- Clamp each dimension ----
    for name, val in [("structure", structure_score),
                      ("style", style_score),
                      ("semantics", semantics_score),
                      ("risk", risk_score)]:
        locals()[f"{name}_score"] = max(0, min(100, val))

    # ---- Overall score (weighted) ----
    # You can tune these weights to your taste.
    overall = (
        structure_score * 0.3 +
        style_score * 0.25 +
        semantics_score * 0.3 +
        risk_score * 0.15
    )
    overall = int(round(overall))
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
    
    # Example structure only — DELETE or OVERWRITE this whole block:
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()
    
    # ←←← Your real logic starts here ←←←
    # Example: perplexity calc, entropy, CodeBERT inference, soul heuristic rules, etc.
    # ...
    # ...
    
    # Final return – must match this format
    return {
        'ai_probability': 0.0,          # REPLACE with your computed float 0–1
        'verdict': 'UNKNOWN',           # REPLACE with 'HUMAN' / 'AI' / 'MIXED' etc.
        'soul_score': None,             # optional float
        'confidence': None              # optional float
    }

# =============================================================
# ===     BATCH SCANNING LOGIC – DO NOT MODIFY BELOW     =====
# =============================================================

def batch_scan(
    input_path: str,
    output_dir: str = "vata_results",
    extensions=('.py', '.js', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.java', '.go', '.rs'),
    ai_threshold: float = 0.78
):
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        print(f"Error: Path not found → {input_path}")
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_path = output_dir / f"vata-scan-{timestamp}.csv"
    errors_log = output_dir / f"errors-{timestamp}.txt"

    results = []
    error_files = []

    # Collect files
    all_files = []
    if input_path.is_file():
        all_files = [input_path]
    else:
        for ext in extensions:
            all_files.extend(input_path.rglob(f"*{ext}"))

    if not all_files:
        print("No matching code files found.")
        return None

    print(f"\nVATA Batch Scan – {len(all_files)} files")
    print(f"  Target: {input_path}")
    print(f"  Output: {csv_path}")
    print("  Starting...\n")

    for file_path in tqdm(all_files, desc="Scanning", unit="file", ncols=100):
        try:
            res = run_vata_analysis(str(file_path))
            
            row = {
                'full_path': str(file_path),
                'filename': file_path.name,
                'ai_probability': res.get('ai_probability'),
                'verdict': res.get('verdict', 'UNKNOWN'),
                'soul_score': res.get('soul_score'),
                'confidence': res.get('confidence'),
                'scan_time': datetime.now().isoformat()
            }
            results.append(row)

            if row['ai_probability'] is not None and row['ai_probability'] >= ai_threshold:
                print(f"  HIGH AI → {file_path.name:<40} ({row['ai_probability']:.3f})")

        except Exception as e:
            error_files.append((str(file_path), str(e)))
            print(f"  Error  → {file_path.name}")

    # Save & summarize
    if results:
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"\nResults saved → {csv_path}")

        print("\n" + "═" * 70)
        print("SUMMARY")
        print("═" * 70)
        print(df['verdict'].value_counts().to_string())
        
        if 'ai_probability' in df and df['ai_probability'].notna().any():
            print(f"\nAI prob stats:")
            print(f"  Mean:   {df['ai_probability'].mean():.3f}")
            print(f"  Median: {df['ai_probability'].median():.3f}")
            print(f"  ≥{ai_threshold}: {len(df[df['ai_probability'] >= ai_threshold])} files")
        print("═" * 70)

    if error_files:
        with open(errors_log, 'w', encoding='utf-8') as f:
            for fp, err in error_files:
                f.write(f"{fp}\n  → {err}\n\n")
        print(f"\n{len(error_files)} errors logged → {errors_log}")

    return df if results else None


# =============================================================
# ===                   RUN IT HERE                          ===
# =============================================================

if __name__ == "__main__":
    # ←←← CHANGE THIS to your actual test folder or file ←←←
    target = r"C:\Users\Leroy\Documents\vata_test_folder"   # example

    # Or test single file:
    # target = r"C:\path\to\example.py"

    batch_scan(target)
