# vata_humanizer.py
# UPDATED VERSION - Enhanced with refined scoring, personalities, stronger guardians, chaos bonuses
# Based on original vatahumanizer.py with additions for better separation, contextual humanization, and risk blocking
# Run: python vata_humanizer.py [--personality chaotic] [--level rage] [--target 80] [code]

import random
import sys
import argparse
import difflib
import libcst as cst
import re
from typing import Dict, Optional, List
from statistics import stdev

class ChaosTransformer(cst.CSTTransformer):
    def __init__(self, chaos_level: str = "medium", personality: str = "chaotic"):
        self.chaos_level = chaos_level.lower()
        self.personality = personality.lower()
        self.intensity = {"low": 0.1, "medium": 0.3, "high": 0.6, "rage": 0.9}.get(self.chaos_level, 0.3)

        # Personality profiles
        profiles = {
            "chaotic": {
                "rename_prob": 0.55 * self.intensity,
                "comment_prob": 0.65 * self.intensity,
                "dead_code_prob": 0.45 * self.intensity,
                "slang_prob": 0.9 if self.chaos_level in ["high", "rage"] else 0.5,
                "phrases": ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet", "why am i still awake", "this is cursed but it works", "blame past-me"],
                "emojis": ["😂", "💀", "🔥", "🤡", "🗿", "🚀", "😭", "🧑‍💻", "🤓"],
                "use_emoji": True,
                "var_names": ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow", "gyattEnergy"],
                "profanity": ["damn", "hell", "wtf", "crap"]  # Mild for now
            },
            "professional": {
                "rename_prob": 0.2 * self.intensity,
                "comment_prob": 0.8 * self.intensity,
                "dead_code_prob": 0.1 * self.intensity,
                "slang_prob": 0.1,
                "phrases": ["Note:", "Improvement opportunity:", "Consider refactoring:", "Temporary solution:", "Optimized for performance"],
                "emojis": [],
                "use_emoji": False,
                "var_names": ["tempValue", "resultCounter", "inputParam", "outputVar", "helperFunction"],
                "profanity": []
            },
            "poetic": {
                "rename_prob": 0.4 * self.intensity,
                "comment_prob": 0.7 * self.intensity,
                "dead_code_prob": 0.3 * self.intensity,
                "slang_prob": 0.3,
                "phrases": ["In the dance of bits:", "Whispers of code:", "Eternal loop of fate:", "Shadows of variables:", "Harmony in chaos:"],
                "emojis": ["🌌", "✨", "🌙", "📜", "🕊️"],
                "use_emoji": True,
                "var_names": ["etherealGlow", "cosmicEcho", "lunarWhisper", "stellarPath", "voidHarmony"],
                "profanity": []
            }
        }
        self.style_profile: Dict[str, any] = profiles.get(self.personality, profiles["chaotic"])

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        if random.random() < self.style_profile["rename_prob"]:
            return cst.Name(value=random.choice(self.style_profile["var_names"]))
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["phrases"])
            if self.style_profile["use_emoji"] and random.random() < 0.8:
                flair += " " + random.choice(self.style_profile["emojis"])
            if random.random() < 0.2 and self.style_profile["profanity"]:
                flair += " " + random.choice(self.style_profile["profanity"])
            return cst.Comment(value=f"{updated_node.value.strip()}  # {flair}")
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Add personality-specific comment on functions
        comment_text = f"# {self.personality.upper()} FUNCTION: {random.choice(self.style_profile['phrases'])}"
        if self.style_profile["use_emoji"]:
            comment_text += f" {random.choice(self.style_profile['emojis'])}"
        comment = cst.Comment(value=comment_text)
        new_body = updated_node.body.with_changes(
            header=updated_node.body.header.with_changes(comments=[comment])
        )
        updated_node = updated_node.with_changes(body=new_body)

        # Dead code
        if random.random() < self.style_profile["dead_code_prob"]:
            dead_stmt = cst.Expr(value=cst.Name("pass"))
            dead_line = cst.SimpleStatementLine(
                body=[dead_stmt],
                trailing_whitespace=cst.TrailingWhitespace(),
            )
            new_body = updated_node.body.with_changes(body=[dead_line] + list(updated_node.body.body))
            updated_node = updated_node.with_changes(body=new_body)

        return updated_node


class VataHumanizer:
    def __init__(self, chaos_level: str = "medium", personality: str = "chaotic", target_soul_score: int = 75, max_iterations: int = 5, personalize_from: Optional[str] = None):
        self.chaos_level = chaos_level
        self.personality = personality
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations
        self.personalize_from = personalize_from

    def _run_guardian_checks(self, code: str) -> List[str]:
        violations = []
        risky_patterns = [
            r'eval\(',  # eval calls
            r'exec\(',  # exec calls
            r'os\.system\(',  # os.system
            r'subprocess\.',  # subprocess imports/calls
            r'rm -rf',  # Dangerous shell commands
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI-like API keys
            r'AKIA[0-9A-Z]{16}',  # AWS access keys
            r'Bearer [a-zA-Z0-9\._-]{20,}',  # Bearer tokens
            r'password\s*=\s*["\'].*["\']',  # Hardcoded passwords
            r'http[s]?://.*token=.*',  # URLs with tokens
        ]
        for pattern in risky_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                violations.append(pattern)
        return violations

    def _get_soul_score(self, code: str) -> Dict[str, any]:
        lines = code.splitlines()
        comment_count = sum(1 for line in lines if line.strip().startswith('#'))
        todo_hack_count = sum(1 for line in lines if re.search(r'TODO|HACK|FIXME', line, re.IGNORECASE))
        emoji_count = sum(1 for char in code if char in "😂💀🔥🤡🗿🚀😭🧑‍💻🤓🌌✨🌙📜🕊️")
        profanity_count = sum(code.lower().count(word) for word in ["damn", "hell", "wtf", "crap", "shit", "fuck"])  # Add more if needed
        slang_bonus = sum(code.lower().count(w) * 7 for w in ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao", "skibidi", "rizz", "sigma", "gyatt", "yeet"])
        rename_bonus = sum(code.count(var) * 10 for var in ["bruhMoment", "ngmiVar", "lolzies", "basedCounter", "frfrVal", "skibidiX", "rizzLevel", "sigmaFlow", "gyattEnergy", "etherealGlow", "cosmicEcho"])  # Include from profiles
        length_bonus = len(code) // 15
        short_bonus = 30 if len(lines) < 5 else 0

        # Chaos/entropy bonus
        indent_levels = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        line_lengths = [len(line) for line in lines if line.strip()]
        entropy_bonus = int(stdev(indent_levels) * 5) + int(stdev(line_lengths) * 2) if len(indent_levels) > 1 else 0

        # AI penalties
        single_letter_vars = len(re.findall(r'\b[a-z]\b', code)) > 5  # Too many i,j,k
        no_comments = comment_count == 0
        perfect_structure = all(len(line.strip()) > 0 for line in lines) and len(set(line_lengths)) < 3  # Uniform lines
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

    def humanize(self, code: str) -> str:
        violations = self._run_guardian_checks(code)
        if violations:
            raise ValueError(f"REJECTED: {len(violations)} violations found (e.g., {', '.join(violations[:3])})")

        # Pre-chaos for short code
        if len(code.splitlines()) <= 3 and self.chaos_level == "rage":
            code = f"# {self.personality.upper()} ONE-LINER: {random.choice(self.style_profile['phrases'] if hasattr(self, 'style_profile') else ['ngmi', 'based af', 'frfr'])} {random.choice(['😂', '🔥'])}\n" + code

        current = code.strip()
        best = current
        best_score = self._get_soul_score(current)["score"]

        for i in range(self.max_iterations):
            try:
                tree = cst.parse_module(current)
                transformer = ChaosTransformer(self.chaos_level, self.personality)
                new_tree = tree.visit(transformer)
                new_code = new_tree.code.strip()

                score = self._get_soul_score(new_code)["score"]
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
    print("".join(diff).strip() or "No changes")


def main():
    parser = argparse.ArgumentParser(description="Vata Humanizer - Make AI code human again (Updated with personalities & guardians)")
    parser.add_argument("code", nargs="?", default=None, help="Code or file path")
    parser.add_argument("--level", default="rage", choices=["low", "medium", "high", "rage"])
    parser.add_argument("--personality", default="chaotic", choices=["chaotic", "professional", "poetic"])
    parser.add_argument("--target", type=int, default=75)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--github", default=None, help="GitHub username for style")
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("--why-humanized", action="store_true", help="Explain changes (uses diff)")
    parser.add_argument("--file", action="store_true", help="Input is file path")
    parser.add_argument("--block-risky", action="store_true", help="Block humanization if risky code found")

    args = parser.parse_args()

    if args.code is None:
        code = sys.stdin.read().strip()
    elif args.file:
        with open(args.code, "r") as f:
            code = f.read()
    else:
        code = args.code

    if not code:
        print("No code. Examples:")
        print("  python vata_humanizer.py \"def add(a,b): return a+b\" --personality poetic")
        print("  echo \"print('hi')\" | python vata_humanizer.py --level rage --personality chaotic")
        sys.exit(0)

    humanizer = VataHumanizer(
        chaos_level=args.level,
        personality=args.personality,
        target_soul_score=args.target,
        max_iterations=args.iterations,
        personalize_from=args.github,
    )

    print(f"Humanizing in {args.level} mode with {args.personality} personality (target {args.target}, max {args.iterations} iters)...")

    try:
        humanized = humanizer.humanize(code)
    except ValueError as e:
        if args.block_risky:
            print(e)
            sys.exit(1)
        else:
            print(f"WARNING: {e} - Proceeding anyway since --block-risky not set")
            humanized = code  # Fallback to original

    print("\nORIGINAL:")
    print(code.strip())
    print("─" * 80)

    print("\nHUMANIZED:")
    print(humanized.strip())
    print("─" * 80)

    soul_info = humanizer._get_soul_score(humanized)
    print(f"SOUL SCORE: {soul_info['score']}/100")
    print(f"TIER: {soul_info['tier']}")
    print("METRICS BREAKDOWN:")
    for k, v in soul_info['metrics'].items():
        print(f"  {k}: {v}")

    if soul_info['score'] >= args.target:
        print("TARGET REACHED! Code has SOUL")
    else:
        print(f"Score below target ({soul_info['score']} < {args.target})")

    if args.diff or args.why_humanized:
        print("\nDIFF (Why Humanized):")
        print_diff(code, humanized)


if __name__ == "__main__":
    main()
