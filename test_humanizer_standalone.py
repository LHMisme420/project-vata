# humanizer.py
# Complete fixed version - no more style_profile AttributeError
# January 28, 2026

import random
import libcst as cst
from typing import Optional

class ChaosTransformer(cst.CSTTransformer):
    """Visitor that applies chaotic human-like changes"""

    def __init__(
        self,
        chaos_level: str = "medium",
        personalize_from: Optional[str] = None
    ):
        self.chaos_level = chaos_level.lower()
        self.personalize_from = personalize_from

        # Chaos intensity (probability multipliers)
        self.intensity = {
            "low":    0.10,
            "medium": 0.30,
            "high":   0.60,
            "rage":   0.90,
        }.get(self.chaos_level, 0.30)

        # ────────────────────────────────────────────────
        # This is the fix: initialize style_profile here
        # ────────────────────────────────────────────────
        self.style_profile = {
            "rename_prob":          0.30 * self.intensity,
            "comment_prob":         0.40 * self.intensity,
            "add_dead_code_prob":   0.25 * self.intensity,
            "use_emoji":            self.chaos_level == "rage",
            "slang_chance":         0.65 if self.chaos_level in ["high", "rage"] else 0.25,
            "preferred_phrases":    ["lol", "bruh", "ngmi", "based", "wtf", "frfr", "lmao"],
            "emoji_list":           ["😂", "💀", "🔥", "🤡", "🗿", "🚀", "😭"],
        }

        # Optional personalization tweak
        if personalize_from:
            self.style_profile["preferred_phrases"].append(personalize_from[:8].lower())

    def leave_Name(
        self,
        original_node: cst.Name,
        updated_node: cst.Name
    ) -> cst.BaseExpression:
        if random.random() < self.style_profile["rename_prob"]:
            return cst.Name(
                value=random.choice([
                    "xD", "bruhMoment", "ngmiVar", "basedCounter",
                    "lolzies", "frfrCounter", "skibidiVal"
                ])
            )
        return updated_node

    def leave_Comment(
        self,
        original_node: cst.Comment,
        updated_node: cst.Comment
    ) -> cst.Comment:
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["preferred_phrases"])
            if self.style_profile["use_emoji"]:
                flair += " " + random.choice(self.style_profile["emoji_list"])
            return cst.Comment(
                value=f"{updated_node.value.strip()}  # {flair}"
            )
        return updated_node

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        if random.random() < self.style_profile["add_dead_code_prob"]:
            # Insert harmless dead code at the top of the body
            dead = cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.Name("pass"))],
                leading_lines=[cst.EmptyLine()],
                trailing_whitespace=cst.TrailingWhitespace()
            )
            new_body = updated_node.body.with_changes(
                body=[dead] + list(updated_node.body.body)
            )
            return updated_node.with_changes(body=new_body)
        return updated_node


class VataHumanizer:
    """Main humanizer interface"""

    def __init__(
        self,
        chaos_level: str = "medium",
        target_soul_score: int = 75,
        max_iterations: int = 4,
    ):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations

    def _get_soul_score(self, code: str) -> int:
        """Simple mock scorer – replace with real one later"""
        comment_count = code.count("#")
        slang_count = sum(code.lower().count(w) for w in ["lol", "bruh", "ngmi", "based", "wtf"])
        length_bonus = len(code) // 20
        return min(98, 35 + comment_count * 10 + slang_count * 5 + length_bonus)

    def humanize(self, code: str) -> str:
        current = code.strip()
        best = current
        best_score = self._get_soul_score(current)

        for i in range(self.max_iterations):
            try:
                tree = cst.parse_module(current)
                transformer = ChaosTransformer(chaos_level=self.chaos_level)
                modified_tree = tree.visit(transformer)
                new_code = modified_tree.code.strip()

                score = self._get_soul_score(new_code)
                if score > best_score:
                    best = new_code
                    best_score = score

                if score >= self.target_soul_score:
                    break

                current = new_code

            except Exception as e:
                print(f"Iteration {i+1} failed: {type(e).__name__} – {e}")
                continue

        return best


# Quick test when running the file directly
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
    print(example.strip())
    print("\nHumanized:")
    print(h.humanize(example))
