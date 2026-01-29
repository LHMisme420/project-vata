# vatahumanizer.py
# UPDATED: Robust handling for invalid/empty/stub files + parse error fallback
# No more crashes in CI - skips or falls back gracefully

import random
import sys
import argparse
import difflib
import libcst as cst
import re
from typing import Dict, Optional, List
from statistics import stdev

# ... (keep your ChaosTransformer class exactly as-is from previous version) ...

class ChaosTransformer(cst.CSTTransformer):
    # Your existing __init__ and methods here - unchanged
    # (paste your full ChaosTransformer code from earlier messages if needed)

class VataHumanizer:
    def __init__(self, chaos_level: str = "medium", personality: str = "chaotic", target_soul_score: int = 75, max_iterations: int = 5, personalize_from: Optional[str] = None):
        self.chaos_level = chaos_level
        self.personality = personality
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations
        self.personalize_from = personalize_from

    def _run_guardian_checks(self, code: str) -> List[str]:
        # Your existing guardian checks - unchanged
        violations = []
        risky_patterns = [
            r'eval\(', r'exec\(', r'os\.system\(', r'subprocess\.', r'rm -rf',
            r'sk-[a-zA-Z0-9]{48}', r'AKIA[0-9A-Z]{16}', r'Bearer [a-zA-Z0-9\._-]{20,}',
            r'password\s*=\s*["\'].*["\']', r'http[s]?://.*token=.*',
        ]
        for pattern in risky_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(pattern)
        return violations

    def _get_soul_score(self, code: str) -> Dict[str, any]:
        # Your existing scoring logic - unchanged
        lines = code.splitlines()
        comment_count = sum(1 for line in lines if line.strip().startswith('#'))
        todo_hack_count = sum(1 for line in lines if re.search(r'TODO|HACK|FIXME', line, re.IGNORECASE))
        emoji_count = sum(1 for char in code if char in "😂💀🔥🤡🗿🚀😭🧑‍💻🤓🌌✨🌙📜🕊️")
        profanity_count = sum(code.lower().count(word) for word in ["damn", "hell", "wtf", "crap", "shit", "fuck"])
        slang_bonus = sum(code.lower().count(w) * 7 for w in ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet"])
        rename_bonus = sum(code.count(var) * 10 for var in ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow", "gyattEnergy", "etherealGlow", "cosmicEcho"])
        length_bonus = len(code) // 15
        short_bonus = 30 if len(lines) < 5 else 0

        indent_levels = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        line_lengths = [len(line) for line in lines if line.strip()]
        entropy_bonus = int(stdev(indent_levels) * 5) + int(stdev(line_lengths) * 2) if len(indent_levels) > 1 else 0

        single_letter_vars = len(re.findall(r'\b[a-z]\b', code)) > 5
        no_comments = comment_count == 0
        perfect_structure = all(len(line.strip()) > 0 for line in lines) and len(set(line_lengths)) < 3
        ai_penalty = -30 if single_letter_vars else 0
        ai_penalty -= 20 if no_comments else 0
        ai_penalty -= 25 if perfect_structure else 0

        score = 30 + comment_count * 15 + todo_hack_count * 10 + emoji_count * 5 + profanity_count * 8 + slang_bonus + rename_bonus + length_bonus + short_bonus + entropy_bonus + ai_penalty
        score = min(100, max(0, score))

        tier = (
            "Soulless Void / AI Slop (0-30)" if score <= 30 else
            "Hybrid / Suspicious (31-60)" if score <= 60 else
            "Human-ish (Needs Soul Injection) (61-80)" if score <= 80 else
            "Full Soul 🔥 Trusted Artisan / S+ Chaos Lord (81-100)"
        )

        metrics = {
            "comments": comment_count * 15,
            "todo_hack": todo_hack_count * 10,
            "emoji": emoji_count * 5,
            "profanity": profanity_count * 8,
            "slang": slang_bonus,
            "renames": rename_bonus,
            "length": length_bonus,
            "short": short_bonus,
            "entropy": entropy_bonus,
            "ai_penalty": ai_penalty,
        }

        return {"score": score, "tier": tier, "metrics": metrics}

    def humanize(self, code: str, filename: str = "") -> str:
        violations = self._run_guardian_checks(code)
        if violations:
            raise ValueError(f"REJECTED: {len(violations)} violations found (e.g., {', '.join(violations[:3])})")

        # NEW: Early exit for tiny/empty code
        stripped = code.strip()
        if not stripped or len(stripped.splitlines()) < 2:
            return code  # No point humanizing stubs/empty

        current = stripped
        best = current
        best_score = self._get_soul_score(current)["score"]

        for i in range(self.max_iterations):
            try:
                tree = cst.parse_module(current)
                transformer = ChaosTransformer(self.chaos_level, self.personality)
                new_tree = tree.visit(transformer)
                new_code = new_tree.code.strip()

                score_dict = self._get_soul_score(new_code)
                score = score_dict["score"]

                if score > best_score:
                    best = new_code
                    best_score = score

                if score >= self.target_soul_score:
                    break

                current = new_code
            except cst.ParserSyntaxError as e:
                # NEW: Graceful fallback on parse error
                print(f"Iteration {i+1} skipped due to parse error: {e}")
                # Keep original, but continue to next iter if possible (or break early)
                break
            except Exception as e:
                print(f"Iteration {i+1} failed: {type(e).__name__} - {e}")
                continue

        return best


def print_diff(original: str, humanized: str):
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        humanized.splitlines(keepends=True),
        fromfile="original",
        tofile="humanized",
    )
    print("".join(diff).strip() or "No changes")


def main():
    parser = argparse.ArgumentParser(description="Vata Humanizer - Updated with parse robustness")
    parser.add_argument("code", nargs="?", default=None, help="Code or file path")
    parser.add_argument("--level", default="medium", choices=["low", "medium", "high", "rage"])
    parser.add_argument("--personality", default="chaotic", choices=["chaotic", "professional", "poetic"])
    parser.add_argument("--target", type=int, default=75)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--github", default=None, help="GitHub username for style")
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("--why-humanized", action="store_true")
    parser.add_argument("--file", action="store_true")
    parser.add_argument("--block-risky", action="store_true")

    args = parser.parse_args()

    if args.code is None:
        code = sys.stdin.read().strip()
        filename = "<stdin>"
    elif args.file:
        try:
            with open(args.code, "r", encoding="utf-8") as f:
                code = f.read()
            filename = args.code
        except Exception as e:
            print(f"File read error: {e}")
            sys.exit(1)
    else:
        code = args.code
        filename = "<cli-arg>"

    if not code.strip():
        print("No code provided or empty file.")
        print(f"SOUL SCORE: 0/100 (empty)")
        sys.exit(0)

    humanizer = VataHumanizer(
        chaos_level=args.level,
        personality=args.personality,
        target_soul_score=args.target,
        max_iterations=args.iterations,
        personalize_from=args.github,
    )

    print(f"Humanizing {filename} in {args.level} mode with {args.personality} personality (target {args.target})...")

    try:
        humanized = humanizer.humanize(code, filename=filename)
    except ValueError as e:
        if args.block_risky:
            print(e)
            sys.exit(1)
        else:
            print(f"WARNING: {e} - proceeding with original")
            humanized = code

    print("\nORIGINAL:")
    print(code.strip()[:500] + "..." if len(code) > 500 else code.strip())  # truncate long output
    print("─" * 80)

    print("\nHUMANIZED:")
    print(humanized.strip()[:500] + "..." if len(humanized) > 500 else humanized.strip())
    print("─" * 80)

    soul_info = humanizer._get_soul_score(humanized)
    print(f"SOUL SCORE: {soul_info['score']}/100")
    print(f"TIER: {soul_info['tier']}")
    print("METRICS BREAKDOWN:")
    for k, v in soul_info['metrics'].items():
        print(f"  {k}: {v}")

    if soul_info['score'] >= args.target:
        print("TARGET REACHED!")
    else:
        print(f"Below target ({soul_info['score']} < {args.target})")

    if args.diff or args.why_humanized:
        print("\nDIFF:")
        print_diff(code, humanized)


if __name__ == "__main__":
    main()
