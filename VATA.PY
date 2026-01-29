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

# Note: Enhanced VataSoulScorer v2 – now with tiny local embedding-based "AI-likeness" penalty
# Recommended lightweight model: 'sentence-transformers/all-MiniLM-L6-v2'
#   → ~80 MB, fast on CPU, good general embeddings (works reasonably on code snippets)
#   → Download once: SentenceTransformer('all-MiniLM-L6-v2')  (needs internet first time)
#   → After that: fully offline if model is cached (~/.cache/huggingface/)
#
# If you want even smaller/faster alternatives (2026 context):
#   - nomic-ai/nomic-embed-text-v1.5 (matryoshka, good quality)
#   - BAAI/bge-small-en-v1.5
#   - For pure code: jinaai/jina-embeddings-v2-small-en or microsoft/codebert-base (but heavier)
#
# Usage: scorer = VataSoulScorer(embedding_model_name="all-MiniLM-L6-v2")
#        If model fails to load → falls back to heuristic-only

class VataSoulScorer:
    def __init__(self, api_key=None, enable_behavioral=False, embedding_model_name=None):
        self.api_key = api_key or os.getenv("GROK_API_KEY")
        if not self.api_key:
            raise ValueError("Grok API key required. Set GROK_API_KEY env var or pass it.")
        
        # from xai.grok import GrokClient  # ← adjust to your actual Grok/xAI client import
        # self.client = GrokClient(self.api_key)
        self.client = None  # Placeholder – replace with real client
        
        self.enable_behavioral = enable_behavioral
        
        # Obfuscated / jittered weights (7 components now)
        self.obfuscated_weights = self._compute_obfuscated_weights()
        
        self.refinement_passes = 0
        
        # Tiny embedding signal
        self.embedding_model = None
        self.ai_prototype_embedding = None
        if EMBEDDING_AVAILABLE and embedding_model_name:
            try:
                print(f"Loading embedding model: {embedding_model_name} ...")
                self.embedding_model = SentenceTransformer(embedding_model_name)
                
                # Very simple "AI prototype" – average embedding of typical clean AI code patterns
                # In production: compute this from a small corpus of known LLM outputs
                ai_examples = [
                    "def factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    return n * factorial(n-1)",
                    "def is_prime(num):\n    if num < 2: return False\n    for i in range(2, int(num**0.5)+1):\n        if num % i == 0: return False\n    return True",
                    "result = [x**2 for x in range(10) if x % 2 == 0]",
                ]
                embeddings = self.embedding_model.encode(ai_examples, convert_to_tensor=True)
                self.ai_prototype_embedding = embeddings.mean(dim=0)
                print("Embedding signal initialized.")
            except Exception as e:
                print(f"Embedding init failed: {e}\n→ falling back to heuristic-only mode")
                self.embedding_model = None

    def _compute_obfuscated_weights(self):
        base = [0.22, 0.18, 0.14, 0.12, 0.12, 0.08, 0.08, 0.06]  # comment, quirky, structure, entropy, anti-pattern, behavioral, embedding, jitter
        seed = int(hashlib.sha256(str(random.random()).encode()).hexdigest(), 16) % 1000
        return [w + random.uniform(-0.025, 0.025) * (seed / 500.0) for w in base]

    def _get_embedding_distance(self, code_str):
        if not self.embedding_model or not self.ai_prototype_embedding is not None:
            return 0.0  # neutral if unavailable
        
        try:
            code_emb = self.embedding_model.encode([code_str], convert_to_tensor=True)[0]
            sim = cosine_similarity(
                code_emb.unsqueeze(0),
                self.ai_prototype_embedding.unsqueeze(0)
            ).item()
            # Convert similarity [0–1] → penalty [0–1] where 1=very AI-like → high penalty
            ai_likeness_penalty = max(0.0, sim - 0.4) / 0.6   # threshold ~0.4, full penalty above ~1.0 sim
            return ai_likeness_penalty
        except:
            return 0.0

    def analyze_code(self, code_str):
        scores = {}
        
        # 1. Comment density
        lines = [line for line in code_str.split('\n') if line.strip()]
        comment_lines = sum(1 for line in code_str.split('\n') if re.match(r'^\s*#', line))
        scores['comment_density'] = min(1.0, comment_lines / max(1, len(lines)))
        
        # 2. Quirky identifiers
        vars_found = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_str)
        if vars_found:
            lengths = np.array([len(v) for v in vars_found])
            quirky = stdev(lengths) / max(1e-6, np.mean(lengths)) if len(lengths) > 1 else 0
            quirky += 0.25 * sum(1 for v in vars_found if '_' in v or any(c.isdigit() for c in v))
            scores['quirky_vars'] = min(1.0, quirky / 3.0)  # normalize roughly
        else:
            scores['quirky_vars'] = 0.0
        
        # 3. Structural complexity via AST
        try:
            tree = ast.parse(code_str)
            max_depth = self._ast_max_depth(tree)
            node_count = sum(1 for _ in ast.walk(tree))
            branchy = node_count / max(1, len(lines))
            scores['structure'] = min(1.0, 0.08 * max_depth + 0.04 * branchy)
        except:
            scores['structure'] = 0.15
        
        # 4. Formatting entropy
        indents = [len(line) - len(line.lstrip()) for line in lines]
        lengths = [len(line) for line in lines]
        ent = (variance(indents) if indents else 0) + (stdev(lengths) / 40 if lengths else 0)
        scores['entropy'] = min(1.0, ent / 8.0)  # rough normalization
        
        # 5. Anti-pattern / human smells reward
        human_smells = len(re.findall(r'(?i)#\s*(TODO|HACK|FIXME|NOTE|XXX)', code_str))
        human_smells += len(re.findall(r'print\s*\(\s*["\']debug', code_str))
        uniform_comment = all(5 < len(c.strip()) < 30 for c in re.findall(r'#.*', code_str)) and human_smells == 0
        scores['anti_patterns'] = min(1.0, human_smells * 0.12 - (0.35 if uniform_comment else 0))
        
        # 6. Behavioral (optional / dangerous)
        if self.enable_behavioral:
            scores['behavioral'] = self._run_behavioral_checks(code_str)
        else:
            scores['behavioral'] = 0.5
        
        # 7. NEW: Embedding-based AI-likeness penalty (0 = human-like, 1 = very AI-like)
        embedding_penalty = self._get_embedding_distance(code_str)
        scores['embedding_ai_penalty'] = embedding_penalty
        
        # Weighted sum
        component_scores = [
            scores['comment_density'],
            scores['quirky_vars'],
            scores['structure'],
            scores['entropy'],
            max(0, scores['anti_patterns']),
            scores['behavioral'],
            1.0 - scores['embedding_ai_penalty'],  # invert: high penalty → low soul contrib
        ]
        
        total = sum(s * w for s, w in zip(component_scores, self.obfuscated_weights[:-1]))
        total += self.obfuscated_weights[-1] * random.uniform(-0.04, 0.04)  # final jitter
        
        # Diminishing returns on repeated refinement
        total *= (0.94 ** self.refinement_passes)
        
        return round(min(100.0, max(0.0, total * 100.0)), 1), scores

    def _ast_max_depth(self, node, depth=0):
        if not hasattr(node, 'body') and not hasattr(node, 'orelse') and not hasattr(node, 'handlers'):
            return depth
        children = []
        for field in ['body', 'orelse', 'handlers', 'finalbody']:
            val = getattr(node, field, None)
            if val:
                children.extend(val if isinstance(val, list) else [val])
        if not children:
            return depth
        return max(self._ast_max_depth(child, depth + 1) for child in children)

    def _run_behavioral_checks(self, code_str):
        # CAUTION: executes code → only safe snippets!
        try:
            with open('vata_temp_safe.py', 'w', encoding='utf-8') as f:
                f.write(code_str + "\n\n# Safety guard\nassert True")
            result = subprocess.run(
                ['python', 'vata_temp_safe.py'],
                capture_output=True, text=True, timeout=4
            )
            os.unlink('vata_temp_safe.py')
            if result.returncode != 0:
                return 0.35  # crash can be human (or broken)
            # Very basic defensiveness check
            has_assert = 'assert' in code_str.lower()
            has_try = 'try:' in code_str
            return 0.75 if has_assert or has_try else 0.55
        except:
            return 0.4

    def get_grok_roast(self, code_str, score, detailed_scores):
        if not self.client:
            return "Grok roast unavailable (client not set)."
        
        prompt = (
            f"Code soul score: {score}/100. Breakdown: {detailed_scores}\n"
            "Roast humorously why it feels AI-generated or beautifully human. "
            "Suggest 3–5 concrete, funny ways to add more 'soul' / chaos / personality."
        )
        # response = self.client.query(prompt, model="grok-4")
        # return response.get('text', 'Roast generation failed.')
        return "[Simulated roast – integrate real Grok call here]"

    def refine_code(self, code_str):
        self.refinement_passes += 1
        lines = code_str.splitlines()
        if len(lines) < 5:
            return code_str
        
        inserts = random.sample(range(len(lines)), k=min(4, len(lines)//4 + 1))
        quirks = [
            "# TODO: fix when brain is online again",
            "# HACK: yes this is cursed, fight me",
            "    # screaming internally",
            "debug_val = 42  # will remove... probably",
            "    # if you're reading this send coffee",
        ]
        for i in sorted(inserts, reverse=True):
            lines.insert(i + 1, random.choice(quirks))
        
        # occasional formatting mess
        if random.random() < 0.4:
            idx = random.randint(0, len(lines)-1)
            lines[idx] = '    ' + lines[idx].lstrip()  # random extra indent
        
        return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="VATA Soul Scorer – hardened edition with embedding bite")
    parser.add_argument('code_file', nargs='?', default=None, help="Python file to analyze")
    parser.add_argument('--code', type=str, help="Direct code string to analyze")
    parser.add_argument('--model', type=str, default="all-MiniLM-L6-v2",
                        help="SentenceTransformer model name for embedding signal")
    parser.add_argument('--refine', action='store_true')
    parser.add_argument('--behavioral', action='store_true')
    args = parser.parse_args()

    if args.code:
        code = args.code
    elif args.code_file:
        with open(args.code_file, encoding='utf-8') as f:
            code = f.read()
    else:
        parser.print_help()
        return

    scorer = VataSoulScorer(
        enable_behavioral=args.behavioral,
        embedding_model_name=args.model
    )

    score, details = scorer.analyze_code(code)
    roast = scorer.get_grok_roast(code, score, details)

    print(f"\nSoul Score: {score}/100")
    print("Breakdown:", {k: round(v, 3) for k,v in details.items()})
    print("\nGrok-style Roast & Suggestions:\n" + roast)

    if args.refine:
        print("\nRefining (one pass)...")
        refined = scorer.refine_code(code)
        new_score, _ = scorer.analyze_code(refined)
        print(f"Refined soul score: {new_score}/100  (diminishing returns apply on further passes)")
        print("\nRefined code snippet preview:\n" + '\n'.join(refined.splitlines()[:12]) + "\n...")

if __name__ == "__main__":
    main()
