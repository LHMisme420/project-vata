# humanizer.py - FINAL FIXED VERSION - no style_profile AttributeError

import random
import libcst as cst

class ChaosTransformer(cst.CSTTransformer):
    def __init__(self, chaos_level="medium"):
        self.chaos_level = chaos_level.lower()
        
        # The fix: always create style_profile here
        self.style_profile = {
            "rename_prob": 0.25 if self.chaos_level == "rage" else 0.05,
            "comment_prob": 0.35 if self.chaos_level == "rage" else 0.10,
            "add_dead_code_prob": 0.20 if self.chaos_level == "rage" else 0.05,
            "preferred_phrases": ["lol", "bruh", "ngmi", "based", "wtf", "frfr"],
            "emoji_list": ["😂", "💀", "🔥", "🤡"],
        }

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name):
        if random.random() < self.style_profile["rename_prob"]:
            new_name = random.choice(["xD", "bruhVar", "ngmiCounter", "lolz"])
            return cst.Name(new_name)
        return updated_node

    def leave_Comment(self, original_node: cst.Comment, updated_node: cst.Comment):
        if random.random() < self.style_profile["comment_prob"]:
            flair = random.choice(self.style_profile["preferred_phrases"])
            if random.random() < 0.4:
                flair += " " + random.choice(self.style_profile["emoji_list"])
            return cst.Comment(f"{updated_node.value}  # {flair}")
        return updated_node

    def leave_FunctionDef(self, original_node, updated_node):
        if random.random() < self.style_profile["add_dead_code_prob"]:
            dead_code = cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.Name("pass"))]  # harmless pass
            )
            new_body = updated_node.body.with_changes(
                body=[dead_code] + list(updated_node.body.body)
            )
            return updated_node.with_changes(body=new_body)
        return updated_node


class VataHumanizer:
    def __init__(self, chaos_level="medium", target_soul_score=75, max_iterations=3):
        self.chaos_level = chaos_level
        self.target_soul_score = target_soul_score
        self.max_iterations = max_iterations

    def _get_soul_score(self, code: str) -> int:
        comment_count = code.count("#")
        slang_count = sum(code.lower().count(w) for w in ["lol", "bruh", "ngmi", "based", "wtf"])
        return min(98, 40 + comment_count * 10 + slang_count * 6 + len(code) // 30)

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
                print(f"Iter {i+1} failed: {e}")
                continue

        return best
