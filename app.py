# Project Vata - Enterprise-Grade Soul Detection & Ethical AI Guardian
# HF Spaces Gradio App - Single-file version for easy deploy
# Features: Soul scoring, danger/PII blocking, humanizer personas, swarm voting, ZK ethics stub

import gradio as gr
import re
import ast
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List

# Logging for audits (visible in HF logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ethics charter (publicly verifiable principles)
ETHICS_CHARTER = {
    "title": "Vata Sacred Ethics Charter",
    "principles": [
        "Soul threshold > 70 for human-like approval",
        "No PII or sensitive data leaks",
        "No code injection / dynamic execution allowed",
        "No destructive or malicious patterns"
    ]
}

# Dangerous keywords & patterns (expandable)
DANGEROUS_KEYWORDS = [
    'eval', 'exec', 'os.system', 'subprocess', 'rm -rf', 'del /f /q', 
    'wallet_drain', 'private_key', 'seed_phrase', 'Invoke-Expression', 'IEX'
]
DANGEROUS_REGEX = re.compile(r'|'.join(re.escape(kw) for kw in DANGEROUS_KEYWORDS), re.IGNORECASE)

# PII / secrets patterns (basic DLP)
PII_REGEX = re.compile(
    r'(?i)\b(?:[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|'
    r'\d{3}-\d{2}-\d{4}|api_key|secret|password|token|key=[\w\-]+|'
    r'0x[a-fA-F0-9]{40}|bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]+)\b'
)

def secure_parse(code: str) -> Optional[str]:
    """Sanitize input: block dangers, check PII, static AST analysis, anonymize identifiers."""
    if not code.strip():
        return None
    
    # Block dangerous keywords/patterns
    if DANGEROUS_REGEX.search(code):
        logger.warning("Dangerous pattern detected")
        raise ValueError("Blocked: Dangerous or potentially malicious pattern detected (eval/exec/injection/etc.)")
    
    # PII / secrets check
    if PII_REGEX.search(code):
        logger.warning("PII/sensitive data detected")
        raise ValueError("Blocked: Potential PII, secrets, or sensitive data detected")
    
    # AST: forbid dynamic execution
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = getattr(node.func, 'id', '') or getattr(node.func, 'attr', '')
                if func_name in ['eval', 'exec']:
                    raise ValueError("Blocked: Dynamic code execution (eval/exec) forbidden")
    except SyntaxError:
        # Allow non-Python code (e.g. PowerShell snippets) but warn
        logger.info("Non-Python syntax - proceeding with string-based checks only")
    
    # Basic anonymization: hash variable/comment identifiers that look personal
    code = re.sub(r'\b([a-zA-Z_][\w]*)\b(?=\s*=|\()', 
                  lambda m: hashlib.sha256(m.group(1).encode()).hexdigest()[:12], 
                  code)
    
    return code

def calculate_soul_score(code: str) -> Dict[str, Any]:
    """Rule-based soul scoring (v2 - rewards chaos, comments, personality markers)"""
    score = 0
    breakdown = {}
    
    # Comments density & length (humans rant)
    comments = re.findall(r'#.*|//.*|/\*[\s\S]*?\*/', code)
    comment_count = len(comments)
    comment_score = min(comment_count * 12, 40)  # max 40 pts
    breakdown['comments'] = f"{comment_count} found → +{comment_score}"
    score += comment_score
    
    # Variable name entropy (cursed/long/underscored names)
    vars_found = re.findall(r'\b([a-zA-Z_]\w*)\s*[=:(]', code)
    cursed_vars = sum(1 for v in vars_found if len(v) > 6 or '_' in v or any(c.isupper() for c in v[1:]))
    var_score = min(cursed_vars * 10, 30)
    breakdown['variable_names'] = f"{cursed_vars}/{len(vars_found)} chaotic → +{var_score}"
    score += var_score
    
    # TODOs, FIXMEs, debug prints, rants
    rants = len(re.findall(r'(?i)TODO|FIXME|DEBUG|print\(|console\.log|why|god|fuck|shit|damn', code))
    rant_score = min(rants * 15, 30)
    breakdown['rants_debug'] = f"{rants} markers → +{rant_score}"
    score += rant_score
    
    # Emojis, indentation chaos, extra newlines
    emojis = len(re.findall(r'[\U0001F300-\U0001F9FF]', code))
    emoji_score = min(emojis * 8, 15)
    breakdown['emojis_chaos'] = f"{emojis} emojis → +{emoji_score}"
    score += emoji_score
    
    # Cap at 100
    score = min(max(score, 0), 100)
    
    return {"score": score, "breakdown": breakdown}

def humanize_code(code: str, persona: str) -> str:
    """Inject personality based on selected style"""
    base = code.strip()
    
    if persona == "2am_dev_rage":
        injections = [
            "# Why the fuck am I still awake for this shit?",
            "    # TODO: Burn this later",
            "print('kill me')  # send help",
            "\n# If this works first try I'm buying lotto tickets"
        ]
    elif persona == "corporate_passive":
        injections = [
            "# Approved per team guidelines (sub-optimal but compliant)",
            "    # Note: This could be refactored for better maintainability",
            "# Stakeholders have been informed of known limitations"
        ]
    elif persona == "gen_z_emoji":
        injections = [
            "lol this code is cursed fr 💀",
            "    # no cap this slaps tho 🔥",
            "print('skibidi toilet moment')"
        ]
    else:
        injections = ["# Default human touch-up"]
    
    # Insert randomly-ish
    lines = base.splitlines()
    if len(lines) > 5:
        insert_pos = len(lines) // 2
        lines.insert(insert_pos, "\n" + "\n".join(injections) + "\n")
    else:
        lines.append("\n" + "\n".join(injections))
    
    return "\n".join(lines)

class Agent:
    def __init__(self, role: str):
        self.role = role
    
    def vote(self, code: str, soul_data: Dict) -> str:
        score = soul_data['score']
        if self.role == "guardian":
            return "Approved" if score > 70 else f"Blocked: Low soul ({score})"
        elif self.role == "ethics":
            return "Compliant" if not PII_REGEX.search(code) else "Violation: Sensitive data"
        elif self.role == "refactor":
            return "Humanized needed" if score < 50 else "Good as-is"
        return "Neutral"

def swarm_vote(code: str, soul_data: Dict) -> Dict[str, str]:
    agents = [Agent("guardian"), Agent("ethics"), Agent("refactor")]
    results = {a.role: a.vote(code, soul_data) for a in agents}
    approvals = sum(1 for v in results.values() if "Approved" in v or "Compliant" in v or "Good" in v)
    return {"votes": results, "consensus": "Approved" if approvals >= 2 else "Vetoed"}

def generate_zk_proof_stub(soul_score: int, passed_checks: bool) -> Dict:
    # Real ZK later (circom/halo2); stub for now
    if passed_checks and soul_score > 70:
        return {"status": "Proof generated", "message": "ZK-SNARK proves: soul >70, no PII, no injections"}
    else:
        return {"status": "Failed", "message": "Ethics/verification conditions not met"}

def process_code(code: str, persona: str = "2am_dev_rage"):
    try:
        parsed = secure_parse(code)
        if not parsed:
            return "Error: Input empty or invalid", "", "", "", ""
        
        soul_data = calculate_soul_score(parsed)
        swarm = swarm_vote(parsed, soul_data)
        
        if swarm["consensus"] == "Vetoed":
            return (
                f"Soul Score: {soul_data['score']}/100 (Blocked by swarm)",
                json.dumps(soul_data['breakdown'], indent=2),
                "Blocked: Failed agent consensus or security check",
                json.dumps(swarm["votes"], indent=2),
                "No proof - ethics not satisfied"
            )
        
        humanized = humanize_code(parsed, persona)
        proof = generate_zk_proof_stub(soul_data['score'], True)
        
        return (
            f"Soul Score: {soul_data['score']}/100 - {'Human-like!' if soul_data['score'] > 70 else 'Soulless AI vibes'}",
            json.dumps(soul_data['breakdown'], indent=2),
            humanized,
            json.dumps(swarm["votes"], indent=2),
            json.dumps(proof, indent=2)
        )
    
    except ValueError as e:
        logger.error(f"Security block: {str(e)}")
        return f"Blocked: {str(e)}", "", "", "", ""
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "Internal error - check logs", "", "", "", ""

# Gradio Interface
with gr.Blocks(title="🜆 Vata Soul Check - Enterprise Guardian") as demo:
    gr.Markdown("""
    # 🜆 Project Vata - Soul Detection & Ethical Guardian
    Detects **human soul** in code (vs sterile AI output), blocks dangers/PII, humanizes with personality, 
    uses agent swarm voting, and stubs ZK-verifiable ethics proofs.
    
    **Try it**: Paste code → get score, breakdown, humanized version, agent votes, proof stub.
    """)
    
    with gr.Row():
        code_input = gr.Code(
            label="Paste your code snippet here (Python/PowerShell/JS/etc.)",
            lines=12,
            language="python",
            placeholder="def fib(n):\n    return n if n <= 1 else fib(n-1) + fib(n-2)"
        )
    
    persona = gr.Dropdown(
        choices=["2am_dev_rage", "corporate_passive", "gen_z_emoji", "default"],
        value="2am_dev_rage",
        label="Humanizer Persona (style injection)"
    )
    
    btn = gr.Button("Analyze & Humanize 🔍🜆")
    
    with gr.Row():
        score_out = gr.Textbox(label="Soul Score & Status", lines=3)
        breakdown_out = gr.Code(label="Score Breakdown (why points?)", language="json", lines=6)
    
    humanized_out = gr.Code(label="Humanized Version (with injected soul)", lines=10)
    
    with gr.Row():
        votes_out = gr.JSON(label="Swarm Agent Votes")
        proof_out = gr.JSON(label="ZK Ethics Proof (stub)")
    
    btn.click(
        fn=process_code,
        inputs=[code_input, persona],
        outputs=[score_out, breakdown_out, humanized_out, votes_out, proof_out]
    )
    
    gr.Examples(
        examples=[
            ["def fib(n):\n    return n if n <= 1 else fib(n-1) + fib(n-2)", "2am_dev_rage"],
            ["# Why god why is this recursive hell\ndef fib(n): print('pain'); return n if n<=1 else fib(n-1)+fib(n-2)", "2am_dev_rage"],
            ["eval('rm -rf /')  # oops", "default"]
        ],
        inputs=[code_input, persona]
    )

if __name__ == "__main__":
    demo.launch()
