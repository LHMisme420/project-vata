# humanizer.py
# Updated version with defensive style_profile default to fix AttributeError
# Date: January 28, 2026

import random
import libcst as cst
from typing import Optional, Dict, Any

class ChaosTransformer(cst.CSTTransformer):
    """
    CST Transformer that applies chaotic, human-like modifications to code.
    """
    def __init__(
        self,
        chaos_level: str = "medium",
        personalize_from: Optional[str] = None,
        **kwargs
    ):
        self.chaos_level = chaos_level.lower()
        self.personalize_from = personalize_from

        # Chaos intensity mapping
        self.intensity = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.6,
            "rage": 0.85
        }.get(self.chaos_level, 0.3)

        # Default style profile – prevents AttributeError in leave_Name, leave_FunctionDef, etc.
        self.style_profile: Dict[str, Any] = {
            "comment_style": "casual" if self.chaos_level in ["high", "rage"] else "minimal",
            "variable_naming": "meme" if self.chaos_level == "rage" else "readable",
            "use_emoji": self.chaos_level == "rage",
            "add_slang": self.chaos_level in ["high", "rage"],
            "preferred_phrases": ["lol", "bruh", "ngmi", "based", "wtf", "lmao"],
            "comment_probability": 0.35 if self.chaos_level == "rage" else 0.15,
            "rename_probability": 0.25 if self.chaos_level in ["high", "rage"] else 0.08,
            "dead_code_chance": 0.20 if self.chaos_level == "rage" else 0.05,
        }

        # Override defaults with personalization if provided
        if personalize_from:
            # You can implement real GitHub-based personalization here later
            # For now we just add some flavor
            self.style_profile["preferred_phrases"].extend(["yo", "fam", "skibidi"])
            self.style_profile["comment_style"] = "very casual"

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.BaseExpression:
        # Safe access – style_profile now always exists
        profile = self.style_profile

        if random.random() < profile.get("rename_probability", 0.1):
            # Example: occasionally rename variables in rage mode
            new_name = random.choice(["xD", "bruhMoment", "ngmiVar", "basedCounter"])
            return cst.Name(new_name)

        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment) -> cst.Comment:
        if random.random() < self.style_profile["comment_probability"]:
            # Add chaotic flair to existing comments
            flair = random.choice(self.style_profile["preferred_phrases"])
            return cst.Comment(f"{updated_node.value}  # {flair}")
        return updated_node

    # Add more leave_ methods as needed (FunctionDef, SimpleStatementLine, etc.)
    # For now this is minimal to get past the error and start producing output

    # Example: more chaos in function defs
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if self.chaos_level == "rage" and random.random() < 0.15:
            # Add useless but funny decorator
            new_decorators = list(updated_node.decorators)
            new_decorators.append(cst.Decorator(cst.Name("bruh")))
            return updated_node.with_changes(decorators=new_decorators)
        return updated_node


class VataHumanizer:
    """
    Main humanizer class that coordinates the transformation and scoring.
    """
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
        """
        Replace this with your real soul scorer later.
        Currently using a very simple mock.
        """
        comment_count = code.count("#")
        length_bonus = len(code) // 20
        chaos_bonus = sum(code.count(p) * 3 for p in ["lol", "bruh", "wtf", "ngmi"])
        return min(95, 40 + comment_count * 8 + length_bonus + chaos_bonus)

    def humanize(self, code: str) -> str:
        """
        Main method: parse → transform → try to reach target soul score
        """
        original_score = self._get_soul_score(code)
        current_code = code
        best_code = code
        best_score = original_score

        for i in range(self.max_iterations):
            try:
                module = cst.parse_module(current_code)
                transformer = ChaosTransformer(chaos_level=self.chaos_level)
                modified = module.visit(transformer)
                current_code = modified.code

                score = self._get_soul_score(current_code)
                if score > best_score:
                    best_code = current_code
                    best_score = score

                if score >= self.target_soul_score:
                    break

            except Exception as e:
                # If transformation breaks syntax, revert to previous
                print(f"Iteration {i+1} failed: {e}")
                continue

        return best_code


# If run directly (for quick testing)
if __name__ == "__main__":
    humanizer = VataHumanizer(chaos_level="rage", target_soul_score=75)
    example_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6))  # should print 720
"""

    print("Original:")
    print(example_code)
    print("\nHumanized:")
    print(humanizer.humanize(example_code))
