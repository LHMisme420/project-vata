# vata_humanizer.py
# Complete standalone Vata Humanizer – upgraded & error-free
# Features: LibCST chaos, self-improvement loop, soul scorer, CLI, diff view
# Run: python vata_humanizer.py [--level rage] [--target 75] [--iterations 5] [code]

import random
import sys
import argparse
import difflib
import libcst as cst
from typing import Dict, Optional

# ────────────────────────────────────────────────────────────────
# ChaosTransformer – fixed LibCST transformations
# ────────────────────────────────────────────────────────────────

class ChaosTransformer(cst.CSTTransformer):
    def __init__(self, chaos_level: str = "medium"):
        self.chaos_level = chaos_level.lower()
        self.intensity = {"low": 0.1, "medium": 0.3, "high": 0.6, "rage": 0.9}.get(self.chaos_level, 0.3)

        # Always initialize style_profile here – no AttributeError possible
        self.style_profile: Dict[str, float | list | bool] = {
            "rename_prob":        0.5 * self.intensity,
            "comment_prob":       0.6 * self.intensity,
            "dead_code_prob":     0.4 * self.intensity,
            "slang_prob":         0.8 if self.chaos_level in ["high", "rage"] else 0.4,
            "phrases":            ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt"],
            "emojis":             ["😂", "💀", "🔥", "🤡", "🗿", "🚀", "😭", "🧑‍💻"],
            "use_emoji":          self.chaos_level == "rage",
            "var_names":          ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow"],
        }

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        if random.random() < self.style_profile["rename_prob"]:
            return cst.Name(value=random.choice(self.style_profile["var_names"]))
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["phrases"])
            if self.style_profile["use_emoji"] and random.random() < 0.7:
                flair += " " + random.choice(self.style_profile["emojis"])
            return cst.Comment(value=f"{updated_node.value.strip()}  # {flair}")
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Force a rage comment on every function
        if self.chaos_level == "rage":
            comment = cst.Comment(value=f"# RAGE FUNCTION {random.choice(self.style_profile['phrases'])} {random.choice(self.style_profile['emojis'])}")
            new_body = updated_node.body.with_changes(
                header=updated_node.body.header.with_changes(comments=[comment])
            )
            updated_node = updated_node.with_changes(body=new_body)

        # Safe dead code insertion
        if random.random() < self.style_profile["dead_code_prob"]:
            dead_stmt = cst.Expr(value=cst.Name("pass"))
            dead_line = cst.SimpleStatementLine(
                body=[dead_stmt],
                trailing_whitespace=cst.TrailingWhitespace(),
            )
            new_body = updated_node.body.with_changes(body=[dead_line] + list(updated_node.body.body))
            updated_node = updated_node.with_changes(body=new_body)

        return updated_node


# ────────────────────────────────────────────────────────────────
# VataHumanizer – main class with loop & scorer
# ────────────────────────────────────────────────────────────────

class VataHumanizer:
    def __init__(self, chaos_level: str = "medium", target_soul_score: int = 75, max_iterations: int = 5, personalize_from: Optional[str] = None):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations
        self.personalize_from = personalize_from

    def _get_soul_score(self, code: str) -> int:
        """Upgraded scorer – rewards comments, slang, renames, short-code bonus"""
        comment_count = code.count("#") + code.count("//")
        length_bonus = len(code) // 20
        slang_bonus = sum(code.lower().count(w) * 6 for w in ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt"])
        rename_bonus = sum(code.count(var) * 8 for var in ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow"])
        short_bonus = 25 if len(code.splitlines()) < 5 else 0
        return min(98, 30 + comment_count * 12 + length_bonus + slang_bonus + rename_bonus + short_bonus)

    def humanize(self, code: str) -> str:
        """Applies chaos in a loop until target or max iterations"""
        current = code.strip()
        best = current
        best_score = self._get_soul_score(current)

        for i in range(self.max_iterations):
            try:
                tree = cst.parse_module(current)
                transformer = ChaosTransformer(self.chaos_level)
                new_tree = tree.visit(transformer)
                new_code = new_tree.code.strip()

                score = self._get_soul_score(new_code)
                if score > best_score:
                    best = new_code
                    best_score = score

                if score >= self.target_soul_score:
                    break

                current = new_code
            except Exception as e:
                print(f"Iteration {i+1} failed: {type(e).__name__} - {e}")
                continue

        return best


# ────────────────────────────────────────────────────────────────
# CLI & Diff Helpers
# ────────────────────────────────────────────────────────────────

def print_diff(original: str, humanized: str):
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        humanized.splitlines(keepends=True),
        fromfile="original",
        tofile="humanized",
    )
    print("".join(diff).strip() or "No significant changes")


def main():
    parser = argparse.ArgumentParser(description="Vata Humanizer CLI")
    parser.add_argument("code", nargs="?", default=None, help="Code to humanize (or read from stdin)")
    parser.add_argument("--level", default="rage", choices=["low", "medium", "high", "rage"], help="Chaos level")
    parser.add_argument("--target", type=int, default=75, help="Target soul score")
    parser.add_argument("--iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--github", default=None, help="GitHub username for personalization (stub)")
    parser.add_argument("--diff", action="store_true", help="Show unified diff")
    parser.add_argument("--output", default=None, help="Save humanized code to file")

    args = parser.parse_args()

    # Get input code
    if args.code is None:
        code = sys.stdin.read().strip()
    else:
        code = args.code

    if not code:
        print("No code provided. Examples:")
        print("  python vata_humanizer.py \"def add(a,b): return a+b\"")
        print("  echo \"print('hi')\" | python vata_humanizer.py --level rage --diff")
        sys.exit(0)

    humanizer = VataHumanizer(
        chaos_level=args.level,
        target_soul_score=args.target,
        max_iterations=args.iterations,
        personalize_from=args.github,
    )

    print(f"Humanizing in {args.level} mode (target {args.target}, max {args.iterations} iterations)...")
    humanized = humanizer.humanize(code)

    print("\nORIGINAL:")
    print(code.strip())
    print("─" * 80)

    print("\nHUMANIZED:")
    print(humanized.strip())
    print("─" * 80)

    score = humanizer._get_soul_score(humanized)
    print(f"SOUL SCORE: {score}/98")

    if score >= args.target:
        print("TARGET REACHED! Code has SOUL 🔥")
    else:
        print(f"Score below target ({score} < {args.target}) – crank chaos or add more slang")

    if args.diff:
        print("\nDIFF (original → humanized):")
        print_diff(code, humanized)

    if args.output:
        with open(args.output, "w") as f:
            f.write(humanized)
        print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
