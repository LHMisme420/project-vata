# src/vata/core.py
import re
import math
import numpy as np
from typing import Dict, Any
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# Reference centroids (you can expand with more snippets)
AI_CENTROID = model.encode("def clean_function(x):\n    return x * 2\n# Efficient and clear")
HUMAN_CENTROID = model.encode("""def factorial(n):  # TODO: recursion is cursed at 3am
    if n == 0 or n == 1: return 1
    result = 1
    for i in range(2, n+1):
        result *= i
        print(f"dbg: {i} -> {result}")  # remove before prod lol
    return result  # send help""")

HUMAN_MARKERS = {
    'todo': r'(?i)#?\s*TODO|FIXME|XXX|HACK|NOTE',
    'debug': r'(?i)print\s*\(|console\.log\s*\(|debug|dbg|log\.debug',
    'quirky': r'(?i)\b(buggy|shit|fuck|crap|temp|lol|wtf|pls|plsfix|shitty|dumb|hacky|pain|die|kill me)\b',
    'late_night': r'(?i)3am|midnight|cursed|send help|rip|pain',
}

RISK_PATTERNS = {
    'secrets': r'(?i)api[_-]?key|secret|token|password|pwd|passw|bearer\s+[\w\-]+',
    'pii': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'dangerous': r'(?i)eval\(|exec\(|system\(|os\.popen|subprocess.*shell=True|rm -rf',
}

def calculate_entropy(s: str) -> float:
    if not s: return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob if p > 0)

def score_soul(code: str, use_embeddings: bool = True, behavioral: bool = True) -> Dict[str, Any]:
    lines = code.splitlines()
    n_lines = max(1, len(lines))

    metrics = {}

    # Comment density
    comments = len(re.findall(r'#|//|/\*|\*\*', code))
    metrics['comment_density'] = min(1.0, comments / (n_lines * 0.15))

    # Personality markers
    personality = sum(len(re.findall(pat, code)) for pat in HUMAN_MARKERS.values()) / 10.0
    metrics['personality_markers'] = min(1.0, personality)

    # Naming entropy
    vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
    entropies = [calculate_entropy(v) for v in vars]
    metrics['naming_entropy'] = np.mean(entropies) / 4.0 if entropies else 0.0

    # Provenance / behavioral (simple merge/commit markers)
    metrics['provenance_noise'] = 1.0 if re.search(r'<<<\s*HEAD|===\s*|>>>\s*[a-f0-9]+', code) else 0.0

    # Embedding distance (dual centroids)
    if use_embeddings:
        code_emb = model.encode(code)
        dist_ai = util.cos_sim(code_emb, AI_CENTROID)[0][0]
        dist_human = util.cos_sim(code_emb, HUMAN_CENTROID)[0][0]
        metrics['ai_similarity'] = float(dist_ai)
        metrics['human_similarity'] = float(dist_human)

    # Weighted score (adaptive for short code)
    weights = {
        'comment_density': 0.25,
        'personality_markers': 0.20,
        'naming_entropy': 0.15,
        'provenance_noise': 0.10,
        'human_similarity': 0.30,
        'ai_similarity': -0.30,
    }

    raw = sum(metrics.get(k, 0) * w for k, w in weights.items())
    # Adaptive: penalize less on very short code
    length_factor = min(1.0, n_lines / 20.0)  # full weight above 20 lines
    soul_score = max(0, min(100, int(50 + raw * 50 * length_factor)))

    category = "Trusted Artisan" if soul_score >= 85 else "Suspicious" if soul_score <= 40 else "Mixed"

    risks = []
    for key, pat in RISK_PATTERNS.items():
        if re.search(pat, code):
            risks.append(f"{key.upper()} detected")

    return {
        "soul_score": soul_score,
        "category": category,
        "metrics": {k: round(v, 3) for k, v in metrics.items()},
        "risks": risks,
        "explanation": "Multi-signal soul fingerprint – embeddings + behavior + provenance"
    }
