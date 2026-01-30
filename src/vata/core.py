# src/vata/core.py
import re
import json
import math
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load lightweight embedding model (all-MiniLM-L6-v2 is fast & good enough)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Simple regex patterns for personality / human markers
HUMAN_MARKERS = {
    'todo': r'(?i)#?\s*TODO|FIXME|XXX|HACK|NOTE',
    'debug': r'(?i)print\s*\(|console\.log\s*\(|debug|dbg|log\.debug',
    'comment_density': lambda code: len(re.findall(r'#|//|/\*|\*\*', code)) / max(1, code.count('\n')),
    'quirky_names': r'(?i)\b(buggy|shit|fuck|crap|temp|lol|wtf|pls|plsfix|shitty|dumb|hacky)\b',
    'late_night': r'(?i)3am|midnight|cursed|send help|rip|pain|die|kill me',
}

# Risk patterns (expandable)
RISK_PATTERNS = {
    'secrets': r'(?i)api[_-]?key|secret|token|password|pwd|passw|bearer\s+[\w\-]+',
    'pii': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'high_risk': r'(?i)eval\(|exec\(|system\(|os\.popen|subprocess\.call.*shell=True',
}

def calculate_entropy(s: str) -> float:
    """Shannon entropy for variable names / code style messiness."""
    if not s:
        return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob if p > 0)

def extract_code_blocks(code: str) -> List[str]:
    """Split code into logical blocks (functions, classes, etc.) for better embedding."""
    # Naive split – improve with tree-sitter later
    return re.split(r'(def |class |function |async )', code)

def score_soul(code: str, use_embeddings: bool = True) -> Dict[str, Any]:
    lines = code.splitlines()
    n_lines = max(1, len(lines))

    # Heuristic metrics (0-1 scale)
    metrics = {}

    # 1. Comment / personality density
    comments = len(re.findall(r'#|//|/\*', code))
    metrics['comment_density'] = min(1.0, comments / max(1, n_lines * 0.15))  # expect ~15% comments in human code

    # 2. Debug / TODO / quirky markers
    personality_score = 0.0
    for key, pattern in HUMAN_MARKERS.items():
        if callable(pattern):
            val = pattern(code)
            metrics[key] = val if isinstance(val, float) else len(re.findall(pattern, code))
        else:
            count = len(re.findall(pattern, code))
            metrics[key] = count
            personality_score += min(1.0, count / 3)  # cap influence

    metrics['personality_markers'] = personality_score / len(HUMAN_MARKERS)

    # 3. Naming entropy (higher = more varied/human)
    var_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
    name_entropy = np.mean([calculate_entropy(name) for name in var_names]) if var_names else 0.0
    metrics['naming_entropy'] = min(1.0, name_entropy / 4.0)  # ~4 bits typical for human vars

    # 4. Structural messiness (indent variation, line length var)
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    metrics['indent_variation'] = np.std(indents) / 4.0 if indents else 0.0  # normalize

    # 5. Embedding similarity to "clean AI" style (lower similarity = more human)
    if use_embeddings:
        blocks = extract_code_blocks(code)
        if blocks:
            embeddings = model.encode(blocks)
            # Hypothetical "clean AI" prototype embedding (average of known clean snippets)
            # In production: load a reference embedding vector
            clean_ai_emb = model.encode("def clean_function(x): return x * 2")
            sims = util.cos_sim(embeddings, clean_ai_emb)
            metrics['ai_similarity'] = float(np.mean(sims))
        else:
            metrics['ai_similarity'] = 1.0

    # Weighted soul score (0–100)
    weights = {
        'comment_density': 0.25,
        'personality_markers': 0.20,
        'naming_entropy': 0.15,
        'indent_variation': 0.10,
        'ai_similarity': -0.30,  # penalize high AI-likeness
    }
    raw_score = sum(metrics.get(k, 0) * w for k, w in weights.items())
    soul_score = max(0, min(100, int(50 + raw_score * 50)))  # center around 50

    # Category
    if soul_score >= 71:
        category = "Trusted Artisan"
    elif soul_score <= 40:
        category = "Suspicious"
    else:
        category = "Mixed"

    # Risk flags
    risks = []
    for key, pat in RISK_PATTERNS.items():
        matches = re.findall(pat, code)
        if matches:
            risks.append(f"{key.upper()}: {', '.join(matches[:3])}")

    return {
        "soul_score": soul_score,
        "category": category,
        "metrics": {k: round(v, 3) for k, v in metrics.items()},
        "risks": risks,
        "explanation": f"Scored using {len(metrics)} behavioral + embedding signals.",
        "raw_metrics": metrics  # for debugging / future tuning
    }
