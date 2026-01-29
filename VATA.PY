import os
import re
import random
import ast
import numpy as np
import hashlib
from statistics import variance, stdev
import subprocess  # for optional behavioral sandbox (use with caution!)
try:
    import torch
    from torch.nn.functional import cosine_similarity
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("Warning: sentence-transformers or torch not available → embedding signal disabled")

# Note: Fully Enhanced VataSoulScorer v3 – now with:
# - Obfuscated/jittered weights
# - Formatting entropy + anti-patterns + AST structure
# - Diminishing returns on refinement
# - Optional behavioral checks (upgraded with basic defensiveness + edge case simulation)
# - Improved embedding signal: dual ai/human centroids from expanded snippet corpora
# - Provenance proxy: simple git-like history noise detection (e.g., merge markers, commit comments)
# - Ensemble-style sub-scores with adaptive thresholding (basic logistic-inspired weighting)
#
# For embeddings: uses 'all-MiniLM-L6-v2' by default – lightweight, offline after first load
# Expand ai_snippets/human_snippets below with real data for better accuracy
#
# Usage: python vata_scorer.py myfile.py --model all-MiniLM-L6-v2 --behavioral --refine

class VataSoulScorer:
    def __init__(self, api_key=None, enable_behavioral=False, embedding_model_name=None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("Grok API key required. Set GROK_API_KEY env var or pass it.")
        
        # Placeholder for Grok/xAI client – replace with actual import/call
        # from xai.grok import GrokClient
        # self.client = GrokClient(self.api_key)
        self.client = None  # Simulate for now
        
        self.enable_behavioral = enable_behavioral
        
        # Weights: 8 components + jitter
        self.obfuscated_weights = self._compute_obfuscated_weights()
        
        self.refinement_passes = 0
        
        # Embedding setup with expanded centroids
        self.embedding_model = None
        self.ai_centroid = None
        self.human_centroid = None
        if EMBEDDING_AVAILABLE and embedding_model_name:
            try:
                print(f"Loading embedding model: {embedding_model_name} ...")
                self.embedding_model = SentenceTransformer(embedding_model_name)
                
                # Expanded AI snippets (clean LLM-style code – add 50+ real ones)
                ai_snippets = [
                    "def factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    return n * factorial(n-1)",
                    "def is_prime(num):\n    if num < 2: return False\n    for i in range(2, int(num**0.5)+1):\n        if num % i == 0: return False\n    return True",
                    "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        hashmap = {}\n        for i, n in enumerate(nums):\n            diff = target - n\n            if diff in hashmap:\n                return [hashmap[diff], i]\n            hashmap[n] = i",
                    "import requests\ndef fetch_data(url):\n    response = requests.get(url)\n    return response.json()",
                    "def binary_search(arr, target):\n    left, right = 0, len(arr)-1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
                    # Add more: aim for 50+ diverse LLM-generated examples
                ]
                
                # Expanded human snippets (messy, quirky real code – add 50+)
                human_snippets = [
                    "# god this is ugly but it works for now\ndef process_stuff(data):\n    if not data: return 'nada'\n    # TODO: handle errors better\n    try:\n        return sum(d**2 for d in data if d > 0)\n    except:\n        print('debug: oops')\n        return 0",
                    "# 3am special - dont judge\ndef rage_sort(my_list_thing):\n    sorted_version = sorted(my_list_thing)\n    # HACK: reverse if even length idk why\n    if len(sorted_version) % 2 == 0:\n        sorted_version.reverse()\n    return sorted_version",
                    "var_with_underscore_42 = 42\n# screaming internally about this loop\ndef loop_of_doom(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i  # factorial but shhh\n        # print(f'debug {i}: {result}')  # uncomment if broken",
                    "# Merge from feature branch - conflicts resolved manually\ndef combined_func(a, b):\n    # <<<<<<< HEAD\n    return a + b\n    # =======\n    return a * b\n    # >>>>>>> feature/multiply",
                    "# Commit: fixed bug after coffee\ndef safe_divide(x, y):\n    if y == 0:\n        raise ValueError('no zero div u fool')\n    return x / y",
                    # Add more: real pre-2023 GitHub snippets or personal code
                ]
                
                ai_embs = self.embedding_model.encode(ai_snippets, convert_to_tensor=True)
                self.ai_centroid = ai_embs.mean(dim=0)
                
                human_embs = self.embedding_model.encode(human_snippets, convert_to_tensor=True)
                self.human_centroid = human_embs.mean(dim=0)
                
                print("Dual-centroid embedding signal initialized.")
            except Exception as e:
                print(f"Embedding init failed: {e}\n→ falling back to heuristic-only")
                self.embedding_model = None

    def _compute_obfuscated_weights(self):
        base = [0.20, 0.15, 0.12, 0.12, 0.10, 0.10, 0.10, 0.06, 0.05]  # + provenance
        seed = int(hashlib.sha256(str(random.random()).encode()).hexdigest(), 16) % 1000
        return [w + random.uniform(-0.03, 0.03) * (seed / 500.0) for w in base]

    def _get_embedding_penalty(self, code_str):
        if not self.embedding_model or self.ai_centroid is None or self.human_centroid is None:
            return 0.0
        
        try:
            code_emb = self.embedding_model.encode([code_str], convert_to_tensor=True)[0]
            sim_ai = cosine_similarity(code_emb.unsqueeze(0), self.ai_centroid.unsqueeze(0)).item()
            sim_human = cosine_similarity(code_emb.unsqueeze(0), self.human_centroid.unsqueeze(0)).item()
            
            # Human-likeness: [0-1], higher = more human
            human_likeness = (sim_human - sim_ai + 1.0) / 2.0
            return 1.0 - human_likeness  # penalty for AI-likeness
        except:
            return 0.0

    def analyze_code(self, code_str):
        scores = {}
        lines = [line for line in code_str.split('\n') if line.strip()]
        num_lines = max(1, len(lines))
        
        # 1. Comment density
        comment_lines = sum(1 for line in code_str.split('\n') if re.match(r'^\s*(#|""")', line))
        scores['comment_density'] = min(1.0, comment_lines / num_lines)
        
        # 2. Quirky identifiers
        vars_found = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_str)
        if vars_found:
            lengths = [len(v) for v in vars_found]
            quirky = stdev(lengths) / (sum(lengths)/len(lengths) + 1e-6) if lengths else 0
            quirky += 0.2 * (sum(1 for v in vars_found if '_' in v[1:] or any(c.isdigit() for c in v)) / len(vars_found))
            scores['quirky_vars'] = min(1.0, quirky)
        else:
            scores['quirky_vars'] = 0.0
        
        # 3. Structural complexity
        try:
            tree = ast.parse(code_str)
            max_depth = self._ast_max_depth(tree)
            node_count = sum(1 for _ in ast.walk(tree))
            scores['structure'] = min(1.0, (max_depth * 0.1) + (node_count / num_lines * 0.03))
        except SyntaxError:
            scores['structure'] = 0.2  # Light penalty for errors (human?)
        
        # 4. Formatting entropy
        indents = [len(line) - len(line.lstrip(' \t')) for line in lines]
        lengths = [len(line) for line in lines]
        ent_score = (variance(indents) / 5 if indents else 0) + (stdev(lengths) / 50 if lengths else 0)
        scores['entropy'] = min(1.0, ent_score)
        
        # 5. Anti-patterns / human smells
        smells = len(re.findall(r'(?i)#\s*(TODO|HACK|FIXME|XXX|NOTE|DEBUG)', code_str))
        smells += len(re.findall(r'print\s*\(\s*["\']?debug', code_str, re.I))
        uniform_comments = all(10 < len(c.strip()) < 40 for c in re.findall(r'#.*', code_str)) and smells < 2
        scores['anti_patterns'] = min(1.0, max(0.0, smells * 0.15 - (0.4 if uniform_comments else 0)))
        
        # 6. Behavioral resilience
        if self.enable_behavioral:
            scores['behavioral'] = self._run_behavioral_checks(code_str)
        else:
            scores['behavioral'] = 0.5
        
        # 7. Embedding penalty
        scores['embedding_penalty'] = self._get_embedding_penalty(code_str)
        
        # 8. Provenance proxy (git noise, merge markers, commit comments)
        provenance_score = len(re.findall(r'(<<<<<|>>>>>|======|# Merge|# Commit|# Branch)', code_str, re.I)) * 0.2
        provenance_score += 0.1 if re.search(r'# [a-f0-9]{7,40}', code_str) else 0  # hex commit hash
        scores['provenance'] = min(1.0, provenance_score)
        
        # Ensemble: component scores
        component_scores = [
            scores['comment_density'],
            scores['quirky_vars'],
            scores['structure'],
            scores['entropy'],
            scores['anti_patterns'],
            scores['behavioral'],
            1.0 - scores['embedding_penalty'],
            scores['provenance'],
        ]
        
        # Simple "logistic" ensemble: weighted sum with soft sigmoid for extremes
        weighted_sum = sum(s * w for s, w in zip(component_scores, self.obfuscated_weights[:-1]))
        ensemble = 1 / (1 + np.exp(-5 * (weighted_sum - 0.5)))  # sigmoid centering ~0.5
        
        # Jitter + diminishing returns
        ensemble += self.obfuscated_weights[-1] * random.uniform(-0.05, 0.05)
        ensemble *= (0.93 ** self.refinement_passes)
        
        # Adaptive threshold: boost for short code, penalize long uniform
        adaptive_adj = 0.1 if num_lines < 20 else -0.05 if num_lines > 200 else 0
        
        final_score = min(100, max(0, (ensemble + adaptive_adj) * 100))
        return round(final_score, 1), scores

    def _ast_max_depth(self, node, depth=0):
        children = []
        for field in ast.iter_fields(node):
            if isinstance(field[1], list):
                children.extend([n for n in field[1] if isinstance(n, ast.AST)])
            elif isinstance(field[1], ast.AST):
                children.append(field[1])
        if not children:
            return depth
        return max(self._ast_max_depth(c, depth + 1) for c in children)

    def _run_behavioral_checks(self, code_str):
        # Enhanced: basic edge tests + defensiveness
        try:
            with open('vata_temp.py', 'w') as f:
                f.write(code_str + "\n# Safety: pass")
            result = subprocess.run(['python', 'vata_temp.py'], capture_output=True, timeout=5)
            os.remove('vata_temp.py')
            
            if result.returncode != 0:
                return 0.4  # Crashes can be human
            
            # Simple defensiveness proxies
            has_defense = ('assert' in code_str or 'try:' in code_str or 'if ' in code_str and 'raise' in code_str)
            has_validation = 'isinstance' in code_str or 'type(' in code_str
            
            # Simulate edge: but for real, add hypothesis or manual inputs if func defined
            # For now: reward if no obvious fails
            return 0.85 if has_defense and has_validation else 0.7 if has_defense else 0.55
        except:
            return 0.45

    def get_grok_roast(self, code_str, score, detailed_scores):
        if not self.client:
            return "[Simulated Grok roast: Your code has soul but needs more chaos! Add rants.]"
        
        prompt = f"Code: {code_str[:500]}...\nScore: {score}/100\nDetails: {detailed_scores}\nRoast humorously, suggest quirky improvements."
        # response = self.client.query(prompt, model="grok-4")
        # return response['text']
        return "[Roast placeholder]"

    def refine_code(self, code_str):
        self.refinement_passes += 1
        lines = code_str.split('\n')
        num_inserts = min(5, len(lines)//3)
        insert_idxs = random.sample(range(len(lines)), num_inserts)
        
        quirks = [
            "# TODO: optimize when not lazy",
            "# HACK: temporary fix, sue me",
            "    # internal screaming",
            "# Merge conflict resolved - yay",
            "debug_print = lambda x: print(f'debug: {x}')  # helper",
            "# Commit: v1.2 - added soul",
        ]
        
        for idx in sorted(insert_idxs, reverse=True):
            lines.insert(idx, random.choice(quirks))
        
        # Random mess: extra indent or blank
        if random.random() < 0.5:
            lines[random.randint(0, len(lines)-1)] = '  ' + lines[random.randint(0, len(lines)-1)].lstrip()
        
        return '\n'.join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced VATA Soul Scorer – contender edition")
    parser.add_argument('code_file', nargs='?', help="Path to code file")
    parser.add_argument('--code', help="Direct code string")
    parser.add_argument('--model', default='all-MiniLM-L6-v2', help="Embedding model")
    parser.add_argument('--refine', action='store_true')
    parser.add_argument('--behavioral', action='store_true')
    args = parser.parse_args()
    
    code = args.code or (open(args.code_file).read() if args.code_file else input("Enter code: "))
    
    scorer = VataSoulScorer(enable_behavioral=args.behavioral, embedding_model_name=args.model)
    score, details = scorer.analyze_code(code)
    roast = scorer.get_grok_roast(code, score, details)
    
    print(f"Soul Score: {score}/100")
    print("Details:", {k: round(v, 2) for k, v in details.items()})
    print("Roast:", roast)
    
    if args.refine:
        refined = scorer.refine_code(code)
        new_score, _ = scorer.analyze_code(refined)
        print(f"Refined Score: {new_score}/100")
        print("Refined Code Preview:\n" + refined[:300] + "...")

if __name__ == "__main__":
    main()
