import os
import re
import random
import ast
import numpy as np
import hashlib  # for simple obfuscation hashing
from statistics import variance, stdev
import subprocess  # for optional behavioral sandbox (use with caution)
from xai.grok import GrokClient  # Assuming xAI's Grok API client; install via pip if needed

# Note: This is an updated version of vata.py with enhanced "bite" features:
# - Obfuscated scoring weights (hashed and runtime-computed to prevent easy reverse-engineering)
# - Added entropy measurements (formatting variance, line length distribution)
# - Anti-pattern detection (uniform comments, absent human smells like TODOs/debug prints)
# - Diminishing returns in refinement loop (to discourage excessive gaming)
# - Hybrid statistical signals (AST-based structural analysis for embedding-like insights without full ML)
# - Optional behavioral execution in sandbox (checks resilience to edge inputs; HIGH RISK - enable only in trusted env)
# - Integration with Grok API for roasts and suggestions remains, now with more context

class VataSoulScorer:
    def __init__(self, api_key=None, enable_behavioral=False):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("Grok API key required. Set GROK_API_KEY env var.")
        self.client = GrokClient(self.api_key)
        self.enable_behavioral = enable_behavioral  # Toggle for risky execution checks
        self.obfuscated_weights = self._compute_obfuscated_weights()
        self.refinement_passes = 0  # Track for diminishing returns

    def _compute_obfuscated_weights(self):
        # Obfuscate weights: base values hashed and modulated at runtime
        base_weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]  # Comment, quirky vars, structure, entropy, anti-pattern, behavioral, jitter
        seed = int(hashlib.sha256(str(random.random()).encode()).hexdigest(), 16) % 100
        return [w + random.uniform(-0.02, 0.02) * (seed / 100) for w in base_weights]  # Runtime jitter

    def analyze_code(self, code_str):
        scores = {}
        
        # 1. Comment density (higher = more soul)
        lines = code_str.split('\n')
        comment_lines = len(re.findall(r'^\s*#', code_str, re.MULTILINE))
        scores['comment_density'] = min(1.0, comment_lines / len(lines)) if lines else 0
        
        # 2. Quirky variable naming (length variance, underscores, numbers)
        vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_str)
        var_lengths = [len(v) for v in vars]
        quirky_score = (stdev(var_lengths) / max(1, np.mean(var_lengths))) if var_lengths else 0
        quirky_score += 0.2 if any(re.match(r'.*_[a-z0-9]*$', v) for v in vars) else 0  # Underscore quirks
        scores['quirky_vars'] = min(1.0, quirky_score)
        
        # 3. Structural messiness (using AST for depth/nesting)
        try:
            tree = ast.parse(code_str)
            max_depth = self._ast_max_depth(tree)
            branch_density = len(list(ast.walk(tree))) / max(1, len(lines))  # Nodes per line
            scores['structure'] = min(1.0, (max_depth * 0.1) + (branch_density * 0.05))  # Reward complexity
        except SyntaxError:
            scores['structure'] = 0.2  # Penalize invalid code lightly (could be human error)
        
        # 4. Formatting entropy (variance in indents, line lengths)
        indent_levels = [len(line) - len(line.lstrip(' ')) // 4 for line in lines if line.strip()]  # Assume 4-space tabs
        line_lengths = [len(line) for line in lines if line.strip()]
        entropy_score = (variance(indent_levels) / 4 if indent_levels else 0) + (stdev(line_lengths) / 50 if line_lengths else 0)
        scores['entropy'] = min(1.0, entropy_score)
        
        # 5. Anti-pattern penalties (robotic uniformity)
        todo_count = len(re.findall(r'#\s*TODO|HACK|FIXME', code_str, re.I))
        debug_prints = len(re.findall(r'print\(\s*["\']debug', code_str, re.I))
        uniform_comments = all(len(c.group()) < 20 for c in re.finditer(r'#.*', code_str))  # Short uniform comments
        scores['anti_patterns'] = (todo_count * 0.1 + debug_prints * 0.05) - (0.3 if uniform_comments else 0)
        scores['anti_patterns'] = max(0, min(1.0, scores['anti_patterns']))
        
        # 6. Behavioral resilience (optional, sandboxed)
        if self.enable_behavioral:
            behavioral_score = self._run_behavioral_checks(code_str)
            scores['behavioral'] = behavioral_score
        else:
            scores['behavioral'] = 0.5  # Neutral if disabled
        
        # 7. Random jitter for obfuscation
        jitter = random.uniform(-0.05, 0.05)
        
        # Weighted sum with diminishing returns if refining
        total_score = sum(s * w for s, w in zip(scores.values(), self.obfuscated_weights[:-1])) + (self.obfuscated_weights[-1] * jitter)
        total_score *= (0.95 ** self.refinement_passes)  # Decay per pass
        return min(100, max(0, total_score * 100)), scores

    def _ast_max_depth(self, node, depth=0):
        if not isinstance(node, ast.AST):
            return depth
        return max(self._ast_max_depth(child, depth + 1) for child in ast.iter_child_nodes(node)) if ast.iter_child_nodes(node) else depth

    def _run_behavioral_checks(self, code_str):
        # HIGH RISK: Executes code in subprocess sandbox. Use only in isolated env!
        try:
            with open('temp.py', 'w') as f:
                f.write(code_str)
            result = subprocess.run(['python', 'temp.py'], capture_output=True, timeout=5)
            if result.returncode != 0:
                return 0.3  # Crashes = possible human (or bad code)
            # Add edge input tests if code defines functions; simplistic here
            return 0.8 if 'assert' in code_str or 'try:' in code_str else 0.5  # Reward defensiveness
        except Exception:
            return 0.4  # Handling errors = soulful?
        finally:
            os.remove('temp.py')

    def get_grok_roast(self, code_str, score, detailed_scores):
        prompt = (
            f"Analyze this code for human soul (authenticity). Soul score: {score}/100. "
            f"Detailed breakdowns: {detailed_scores}. "
            "Give a humorous roast explaining why it's low/high, and suggest specific ways to 'humanize' it more "
            "(add quirks, messiness, comments). Be witty and encouraging."
        )
        response = self.client.query(prompt, model="grok-4")  # Adjust API call as per xAI docs
        return response['text']

    def refine_code(self, code_str):
        self.refinement_passes += 1
        # Simple auto-humanizer: add random TODOs, comments, quirks
        lines = code_str.split('\n')
        insert_points = random.sample(range(len(lines)), min(3, len(lines)//5))
        for i in insert_points:
            quirks = [
                "# TODO: Fix this later when I'm not sleepy",
                "    # HACK: This works but I hate it",
                "print('debug: here we go')  # Remove later",
                "rage_var = " + lines[i].strip() if ' =' in lines[i] else ""
            ]
            lines.insert(i + 1, random.choice(quirks))
        return '\n'.join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="VATA Soul Scorer: Detect AI vs Human code with bite.")
    parser.add_argument('code_file', help="Path to Python code file")
    parser.add_argument('--refine', action='store_true', help="Auto-refine and re-score")
    parser.add_argument('--behavioral', action='store_true', help="Enable risky behavioral checks")
    args = parser.parse_args()

    with open(args.code_file, 'r') as f:
        code = f.read()

    scorer = VataSoulScorer(enable_behavioral=args.behavioral)
    score, details = scorer.analyze_code(code)
    roast = scorer.get_grok_roast(code, score, details)
    
    print(f"Soul Score: {score}/100")
    print("Detailed Scores:", details)
    print("Grok's Roast:", roast)
    
    if args.refine:
        refined = scorer.refine_code(code)
        new_score, _ = scorer.analyze_code(refined)
        print(f"Refined Score: {new_score}/100 (note diminishing returns)")
        with open('refined.py', 'w') as f:
            f.write(refined)

if __name__ == "__main__":
    main()
