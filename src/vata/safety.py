import ast
import hashlib
import statistics
from typing import Dict

def get_logic_fingerprint(code: str) -> Dict:
    stats = {'human_score': 0, 'details': {}}
    
    # Strong human comment boost
    comments = [l.lower() for l in code.splitlines() if l.strip().startswith('#')]
    human_keywords = ['todo', 'slow', 'elegant', 'nostalgic', 'maybe', 'soul', 'hack', 'later', 'damn', 'wtf']
    human_comments = sum(any(kw in c for kw in human_keywords) for c in comments)
    
    # AI penalty
    ai_patterns = 0
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.Lambda, ast.AnnAssign)):
                ai_patterns += 1
        if '@' in code or 'lru_cache' in code:
            ai_patterns += 2
    except:
        pass
    
    human_score = 40 + human_comments * 20 - ai_patterns * 10
    human_score = min(100, max(0, human_score))
    
    seal = hashlib.sha256(code.encode()).hexdigest()
    
    return {'human_score': human_score, 'seal': seal, 'message': 'HIGHLY HUMAN 🟢' if human_score >= 70 else 'LIKELY AI 🔶'}

def apply_safety_seal(code: str, fp: Dict) -> dict:
    return {'seal': fp['seal'], 'human_score': fp['human_score']}

def verify_fingerprint(code: str, seal_data: dict) -> tuple[bool, str]:
    current_seal = hashlib.sha256(code.encode()).hexdigest()
    if current_seal != seal_data['seal']:
        return False, 'TAMPERED'
    score = seal_data['human_score']
    return True, f'HUMAN CONFIRMED 🟢 (Score: {score})' if score >= 70 else 'AI SUSPECTED 🔶'
