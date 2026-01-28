#!/usr/bin/env python3
# vata.py - FINAL POLISHED CLI VERSION
# Run like this:
#   python vata.py "your code here"
#   python vata.py --level rage --target 85 "def add(a,b): return a+b"
#   echo "print('hi')" | python vata.py --level rage

import random
import sys
import argparse
import difflib
import libcst as cst
from typing import Dict, Optional

class ChaosTransformer(cst.CSTTransformer):
    def __init__(self, chaos_level: str = "medium"):
        self.chaos_level = chaos_level.lower()
        self.intensity = {"low": 0.1, "medium": 0.3, "high": 0.6, "rage": 0.9}.get(self.chaos_level, 0.3)

        self.style_profile = {
            "rename_prob": 0.6 * self.intensity,
            "comment_prob": 0.7 * self.intensity,
            "dead_code_prob": 0.5 * self.intensity,
            "phrases": ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet"],
            "emojis": ["😂", "💀", "🔥", "🤡", "🗿", "🚀", "😭"],
            "var_names": ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow"],
        }

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        if random.random() < self.style_profile["rename_prob"]:
            return cst.Name(random.choice(self.style_profile["var_names"]))
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["phrases"])
            if random.random() < 0.7:
                flair += " " + random.choice(self.style_profile["emojis"])
            return cst.Comment(f"{updated_node.value.strip()}  # {flair}")
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if self.chaos_level == "rage":
            comment = cst.Comment(f"# RAGE FUNCTION {random.choice(self.style_profile['phrases'])} {random.choice(self.style_profile['emojis'])}")
            new_body = updated_node.body.with_changes(
                header=updated_node.body.header.with_changes(comments=[comment])
            )
            updated_node = updated_node.with_changes(body=new_body)

        if random.random() < self.style_profile["dead_code_prob"]:
            dead_stmt = cst.Expr(cst.Name("pass"))
            dead_line = cst.SimpleStatementLine(
                body=[dead_stmt],
                trailing_whitespace=cst.TrailingWhitespace(),
            )
            new_body = updated_node.body.with_changes(body=[dead_line] + list(updated_node.body.body))
            updated_node = updated_node.with_changes(body=new_body)

        return updated_node


class VataHumanizer:
    def __init__(self, chaos_level="medium", target_soul_score=75, max_iterations=5):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations

    def _get_soul_score(self, code: str) -> int:
        comments = code.count("#") + code.count("//")
        length = len(code) // 15
        slang = sum(code.lower().count(w) * 8 for w in ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt"])
        renames = sum(code.count(v) * 10 for v in ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow"])
        short_bonus = 40 if len(code.splitlines()) < 5 else 0
        return min(98, 30 + comments * 15 + length + slang + renames + short_bonus)

    def humanize(self, code: str) -> str:
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
                print(f"Iteration {i+1} failed: {e}")
                continue

        return best


# ────────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vata Humanizer - Make AI code human again",
        epilog="Examples:\n"
               "  python vata.py \"def add(a,b): return a+b\"\n"
               "  echo \"print('hi')\" | python vata.py --level rage\n"
               "  python vata.py mycode.py --file --output humanized.py"
    )
    parser.add_argument("input", nargs="?", default=None, help="Code string or file path")
    parser.add_argument("--level", default="rage", choices=["low", "medium", "high", "rage"])
    parser.add_argument("--target", type=int, default=75)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output", help="Save to file")
    parser.add_argument("--file", action="store_true", help="Input is file path")
    parser.add_argument("--diff", action="store_true", help="Show diff")

    args = parser.parse_args()

    # Get code
    if args.input is None:
        code = sys.stdin.read().strip()
    elif args.file:
        try:
            with open(args.input, "r") as f:
                code = f.read()
        except FileNotFoundError:
            print("File not found:", args.input)
            sys.exit(1)
    else:
        code = args.input

    if not code:
        parser.print_help()
        sys.exit(0)

    humanizer = VataHumanizer(args.level, args.target, args.iterations)

    print(f"Humanizing in {args.level} mode (target {args.target})...")
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
        print("TARGET REACHED! This code has SOUL 🔥")
    else:
        print(f"Score below target ({score} < {args.target})")

    if args.diff:
        diff = difflib.unified_diff(
            code.splitlines(keepends=True),
            humanized.splitlines(keepends=True),
            fromfile="original",
            tofile="humanized",
        )
        print("\nDIFF:")
        print("".join(diff).strip())

    if args.output:
        with open(args.output, "w") as f:
            f.write(humanized)
        print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
