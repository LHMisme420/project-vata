# vata.py - FINAL POLISHED CLI VERSION
# Fixed LibCST errors, higher chaos, reliable 75–98 scores
# Run: python vata.py "def add(a,b): return a+b" --level rage --target 85 --diff

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

        # Safe profile init – no AttributeError
        self.style_profile: Dict[str, any] = {
            "rename_prob":        0.65 * self.intensity,
            "comment_prob":       0.75 * self.intensity,
            "dead_code_prob":     0.55 * self.intensity,
            "slang_prob":         0.95 if self.chaos_level in ["high", "rage"] else 0.5,
            "phrases":            ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet"],
            "emojis":             ["😂", "💀", "🔥", "🤡", "🗿", "🚀", "😭", "🧑‍💻"],
            "var_names":          ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow", "gyattEnergy"],
        }

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        if random.random() < self.style_profile["rename_prob"]:
            return cst.Name(value=random.choice(self.style_profile["var_names"]))
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["phrases"])
            if random.random() < 0.8:
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

        # Fixed dead code insertion – proper whitespace, no semicolon error
        if random.random() < self.style_profile["dead_code_prob"]:
            dead_stmt = cst.Expr(value=cst.Name("pass"))
            dead_line = cst.SimpleStatementLine(
                body=[dead_stmt],
                leading_lines=[cst.EmptyLine()],
                trailing_whitespace=cst.TrailingWhitespace(),
            )
            new_body = updated_node.body.with_changes(body=[dead_line] + list(updated_node.body.body))
            updated_node = updated_node.with_changes(body=new_body)

        return updated_node


class VataHumanizer:
    def __init__(self, chaos_level: str = "medium", target_soul_score: int = 75, max_iterations: int = 5):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations

    def _get_soul_score(self, code: str) -> int:
        comment_count = code.count("#") + code.count("//")
        length_bonus = len(code) // 15
        slang_bonus = sum(code.lower().count(w) * 8 for w in ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet"])
        rename_bonus = sum(code.count(var) * 10 for var in ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow", "gyattEnergy"])
        short_bonus = 40 if len(code.splitlines()) < 5 else 0
        return min(98, 30 + comment_count * 15 + length_bonus + slang_bonus + rename_bonus + short_bonus)

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
    print("".join(diff).strip() or "No significant changes")


def main():
    parser = argparse.ArgumentParser(description="Vata Humanizer CLI - Make AI code human again")
    parser.add_argument("input", nargs="?", default=None, help="Code string or file path (omit to read stdin)")
    parser.add_argument("--level", default="rage", choices=["low", "medium", "high", "rage"])
    parser.add_argument("--target", type=int, default=75)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--diff", action="store_true", help="Show unified diff")
    parser.add_argument("--output", default=None, help="Save humanized code to file")
    parser.add_argument("--file", action="store_true", help="Input is file path")

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
        print("TARGET REACHED! This code has SOUL 🔥")
    else:
        print(f"Score below target ({score} < {args.target}) – crank chaos or add more slang")

    if args.diff:
        print("\nDIFF (original → humanized):")
        print_diff(code, humanized)

    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(humanized)
            print(f"Saved to {args.output}")
        except Exception as e:
            print("Failed to save:", e)


if __name__ == "__main__":
    main()
