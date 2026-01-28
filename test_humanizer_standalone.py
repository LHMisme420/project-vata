# humanizer.py
# Full updated version – January 28, 2026
# Fixes AttributeError: 'ChaosTransformer' object has no attribute 'style_profile'
# Added default style_profile in __init__ + basic chaos transformations

import random
import libcst as cst
from typing import Optional, Dict, Any

class ChaosTransformer(cst.CSTTransformer):
    """
    Applies chaotic, human-like modifications using LibCST.
    """
    def __init__(
        self,
        chaos_level: str = "medium",
        personalize_from: Optional[str] = None,
        **kwargs
    ):
        self.chaos_level = chaos_level.lower()
        self.personalize_from = personalize_from

        # Chaos intensity scale (0.0–1.0)
        self.intensity = {
            "low":    0.10,
            "medium": 0.30,
            "high":   0.60,
            "rage":   0.85,
        }.get(self.chaos_level, 0.30)

        # ────────────────────────────────────────────────
        # This line fixes the AttributeError you kept getting
        # ────────────────────────────────────────────────
        self.style_profile: Dict[str, Any] = {
            "comment_style":       "casual" if self.chaos_level in ["high", "rage"] else "minimal",
            "variable_naming":     "meme"   if self.chaos_level == "rage" else "readable",
            "use_emoji":           self.chaos_level == "rage",
            "add_slang":           self.chaos_level in ["high", "rage"],
            "preferred_phrases":   ["lol", "bruh", "ngmi", "based", "wtf", "lmao", "frfr"],
            "comment_probability": 0.40 if self.chaos_level == "rage" else 0.15,
            "rename_probability":   0.30 if self.chaos_level in ["high", "rage"] else 0.10,
            "dead_code_chance":    0.25 if self.chaos_level == "rage" else 0.05,
            "emoji_list":          ["😂", "💀", "🔥", "🤡", "🗿", "🚀"],
        }

        # Optional personalization override
        if personalize_from:
            self.style_profile["preferred_phrases"].extend(["yo", "fam", "skibidi", personalize_from[:8]])
            self.style_profile["comment_probability"] += 0.10

    # ────────────────────────────────────────────────
    # Visitor methods – now safe to access self.style_profile
    # ────────────────────────────────────────────────

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        profile = self.style_profile
        if random.random() < profile["rename_probability"]:
            new_name = random.choice(["xD", "bruhMoment", "ngmiVar", "basedCounter", "lolzies", "fr"])
            return cst.Name(new_name)
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        profile = self.style_profile
        if random.random() < profile["comment_probability"]:
            flair = random.choice(profile["preferred_phrases"])
            if profile["use_emoji"]:
                flair += " " + random.choice(profile["emoji_list"])
            return cst.Comment(f"{updated_node.value}  # {flair}")
        return updated_node

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if self.chaos_level == "rage" and random.random() < self.style_profile["dead_code_chance"]:
            # Add useless dead-code line (preserves syntax)
            new_body = list(updated_node.body.body)
            dead_line = cst.Expr(value=cst.Name("pass  # dead code lol"))
            new_body.insert(0, cst.SimpleStatementLine(body=[dead_line]))
            updated_node = updated_node.with_changes(body=updated_node.body.with_changes(body=new_body))
        return updated_node


class VataHumanizer:
    """Main entry point for humanizing code."""

    def __init__(
        self,
        chaos_level: str = "medium",
        target_soul_score: int = 75,
        max_iterations: int = 3,
    ):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations

    def _get_soul_score(self, code: str) -> int:
        """Mock scorer – replace with your real implementation later."""
        comment_count = code.count("#") + code.count("//")
        length_bonus = len(code) // 20
        chaos_bonus = sum(code.lower().count(w) * 4 for w in ["lol", "bruh", "wtf", "ngmi", "based"])
        return min(98, 35 + comment_count * 9 + length_bonus + chaos_bonus)

    def humanize(self, code: str) -> str:
        current_code = code.strip()
        best_code = current_code
        best_score = self._get_soul_score(current_code)

        for i in range(self.max_iterations):
            try:
                module = cst.parse_module(current_code)
                transformer = ChaosTransformer(chaos_level=self.chaos_level)
                modified = module.visit(transformer)
                new_code = modified.code.strip()

                score = self._get_soul_score(new_code)
                if score > best_score:
                    best_code = new_code
                    best_score = score

                if score >= self.target_soul_score:
                    print(f"Target reached after {i+1} iterations (score: {score})")
                    break

                current_code = new_code

            except Exception as e:
                print(f"Iteration {i+1} failed: {type(e).__name__} – {e}")
                continue

        return best_code


# Quick test when running file directly
if __name__ == "__main__":
    h = VataHumanizer(chaos_level="rage", target_soul_score=70)
    example = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6))  # should print 720
"""

    print("Original:")
    print(example)
    print("\nHumanized:")
    print(h.humanize(example))
