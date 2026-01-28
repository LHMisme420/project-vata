import libcst as cst
import libcst.metadata as m
import random
import os
import requests
from typing import Optional, Dict

class VataHumanizer:
    def __init__(self, chaos_level: str = "medium", target_soul_score: int = 80):
        self.chaos_level = chaos_level.lower()  # mild, medium, rage
        self.target_soul_score = target_soul_score
        self.style_profile: Optional[Dict] = None  # Will hold personalized style data

    def personalize_from_github(self, username: str, repo: str = None):
        """Fetch and analyze user's code style from GitHub."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN env var required for personalization.")
        
        # Fetch repos if not specified
        if not repo:
            url = f"https://api.github.com/users/{username}/repos"
            headers = {"Authorization": f"token {token}"}
            repos = requests.get(url, headers=headers).json()
            if repos:
                repo = repos[0]["name"]  # Use first repo as default
        
        # Fetch Python files from repo (simplified: grab one file for MVP)
        url = f"https://api.github.com/repos/{username}/{repo}/contents"
        files = requests.get(url, headers=headers).json()
        py_files = [f for f in files if f["name"].endswith(".py")]
        if not py_files:
            raise ValueError("No Python files found in repo.")
        
        # Download a sample file
        sample_url = py_files[0]["download_url"]
        code = requests.get(sample_url).text
        
        # Analyze style (simple metrics for MVP)
        self.style_profile = {
            "var_naming": self._detect_naming_style(code),  # e.g., snake_case, camelCase
            "comment_freq": code.count("#") / code.count("\n") if code.count("\n") else 0,
            "preferred_constructs": self._detect_constructs(code),  # e.g., loops vs comprehensions
        }
        return self.style_profile

    def _detect_naming_style(self, code: str) -> str:
        # Placeholder: regex to detect snake_case vs camelCase (expand later)
        import re
        snake = len(re.findall(r"[a-z]+_[a-z]+", code))
        camel = len(re.findall(r"[a-z][A-Z]", code))
        return "snake_case" if snake > camel else "camel_case"

    def _detect_constructs(self, code: str) -> Dict:
        # Count loops vs comprehensions
        return {
            "uses_comprehensions": "comprehension" in code,
            "uses_loops": "for " in code or "while " in code,
        }

    def humanize(self, code_str: str) -> str:
        """Main humanization function."""
        # Parse to AST
        tree = cst.parse_module(code_str)
        wrapper = m.MetadataWrapper(tree)
        
        # Apply transformations based on chaos level and style
        transformed = self._apply_chaos(wrapper.module)
        
        # Convert back to string
        humanized_code = transformed.code
        
        # Self-test loop: Re-score and iterate if needed (up to 3 tries)
        for _ in range(3):
            score = self._get_soul_score(humanized_code)  # Replace with your actual scorer
            if score >= self.target_soul_score:
                break
            humanized_code = self._add_more_chaos(humanized_code)
        
        return humanized_code

    def _apply_chaos(self, module: cst.Module) -> cst.Module:
        # Transformer class for AST modifications
        class ChaosTransformer(cst.CSTTransformer):
            def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
                # Add random TODO comment
                if random.random() > 0.5:
                    todo = cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value='"# TODO: Optimize this crap"'))])
                    updated_node = updated_node.with_changes(body=updated_node.body.with_changes(body=[todo] + list(updated_node.body.body)))
                return updated_node
        
        # Apply transformer
        return module.visit(ChaosTransformer())

    def _add_more_chaos(self, code_str: str) -> str:
        # Incremental chaos: Add typos, renames, etc.
        lines = code_str.split("\n")
        for i in range(len(lines)):
            if random.random() < 0.1:  # 10% chance per line
                lines[i] += "  # WTF why does this work?"
        return "\n".join(lines)

    def _get_soul_score(self, code_str: str) -> int:
        # Placeholder: Integrate your actual Vata scorer here
        from vata_scorer import calculate_soul_score  # Assuming your existing module
        return calculate_soul_score(code_str)
