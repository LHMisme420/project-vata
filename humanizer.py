import libcst as cst
import libcst.metadata as m
import random
import os
import requests
from typing import Optional, Dict
import sys
from io import StringIO

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
            score = self._get_soul_score(humanized_code)
            if score >= self.target_soul_score:
                break
            humanized_code = self._add_more_chaos(humanized_code)
        
        # Semantic check (critical!)
        if not self.verify_humanized(code_str, humanized_code):
            # Fallback or error handling
            # For MVP: raise error or return original with warning
            raise ValueError(
                "Humanization broke semantics! Original and humanized outputs differ.\n"
                f"Original output: {self._get_output_preview(code_str)}\n"
                f"Humanized output: {self._get_output_preview(humanized_code)}"
            )
        
        return humanized_code

    def _apply_chaos(self, module: cst.Module) -> cst.Module:
        # Transformer class for AST modifications
        class ChaosTransformer(cst.CSTTransformer):
            METADATA_DEPENDENCIES = (m.PositionProvider,)
            
            def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
                # Add random TODO comment
                if random.random() > 0.5:
                    todo = cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value='"# TODO: Optimize this crap"'))])
                    updated_node = updated_node.with_changes(body=updated_node.body.with_changes(body=[todo] + list(updated_node.body.body)))
                return updated_node
            
            def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
                intensity = self._get_chaos_intensity()  # Access via self (make it class method if needed)
                if random.random() < intensity:
                    # Add rage comment based on level
                    comment = "# This is getting annoying" if intensity < 0.5 else "# Fuck this, it works for now"
                    new_expr = cst.Expr(value=cst.SimpleString(value=f'"{comment}"'))
                    return updated_node.with_changes(body=list(updated_node.body) + [new_expr])
                return updated_node
            
            # Add more: e.g., variable renames
            def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
                if self.style_profile and random.random() < 0.1:
                    if self.style_profile["var_naming"] == "snake_case":
                        return updated_node.with_changes(value=updated_node.value.lower().replace(" ", "_"))
                return updated_node
        
        # Apply transformer
        return module.visit(ChaosTransformer())

    def _get_chaos_intensity(self) -> float:
        if self.chaos_level == "mild": return 0.2
        elif self.chaos_level == "medium": return 0.5
        elif self.chaos_level == "rage": return 0.8
        else: raise ValueError("Invalid chaos level")

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

    def verify_humanized(self, original_code: str, humanized_code: str) -> bool:
        """
        Execute original and humanized code in a sandbox and compare outputs.
        Returns True if they produce the same result (basic semantic preservation check).
        """
        def safe_exec(code: str) -> str:
            try:
                # Sandboxed globals/locals
                local_scope = {}
                # Execute the code
                exec(code, {}, local_scope)
                
                # For simple functions/scripts, look for common output patterns
                # Customize this based on what your typical test code looks like
                if "result" in local_scope:
                    return str(local_scope["result"])
                elif "print" in code:  # crude check for printed output
                    # This is limited; for real use consider capturing stdout
                    old_stdout = sys.stdout
                    redirected_output = sys.stdout = StringIO()
                    try:
                        exec(code, {}, local_scope)
                        return redirected_output.getvalue().strip()
                    finally:
                        sys.stdout = old_stdout
                else:
                    # Default: assume last expression or variable
                    return str(local_scope.get(list(local_scope.keys())[-1], ""))
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        original_output = safe_exec(original_code)
        humanized_output = safe_exec(humanized_code)
        
        # For MVP: exact string match (can improve with fuzzy comparison later)
        return original_output == humanized_output

    # Optional helper for better error messages
    def _get_output_preview(self, code: str) -> str:
        try:
            old_stdout = sys.stdout
            output = sys.stdout = StringIO()
            exec(code, {}, {})
            sys.stdout = old_stdout
            return output.getvalue().strip()[:100] + "..." if output.getvalue() else "No output"
        except:
            return "Execution failed"
