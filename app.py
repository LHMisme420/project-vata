import gradio as gr
import random
import re
import hashlib
import json

def soul_score(code):
    if not code or not code.strip():
        return 0
    score = 0
    lower = code.lower()
    
    # Markers like TODO/FIXME
    if re.search(r'(todo|fixme|hack|note|optimize)', lower, re.IGNORECASE):
        score += 25
    
    # Comments
    score += min(20, len(re.findall(r'#|//|/\*|\*', code)) * 2)
    
    # Debug prints
    if re.search(r'(write-host|console\.log|print|debug)', lower):
        score += 15
    
    # Pipes (common in PowerShell)
    pipe_count = code.count('|')
    if pipe_count > 1:
        score += min(20, pipe_count * 5)
    
    # Aliases (PowerShell specific)
    aliases = len(re.findall(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', lower, re.IGNORECASE))
    if aliases > 2:
        score += 15
    
    # Descriptive variables
    vars_list = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars_list:
        avg_len = sum(len(v) for v in vars_list) / len(vars_list)
        if avg_len > 10:
            score += 15
        elif avg_len > 6:
            score += 8
    
    # Quirky comments
    if re.search(r'sorry|hi mom|lol|coffee|idk|pray', lower):
        score += 10
    
    # Blank lines mess
    blank_ratio = code.count('\n\n') / max(1, len(code.splitlines()))
    if blank_ratio > 0.08:
        score += 10
    
    # Penalty for ultra-clean code
    comment_count = len(re.findall(r'#|//|/\*|\*', code))
    if score < 30 and len(code) > 200 and comment_count == 0:
        score -= 25
    
    return max(0, min(100, score))

def humanize(code, lang="PowerShell", style=""):
    try:
        lines = code.splitlines()
        new_lines = lines[:]

        markers = [
            "# TODO: test later lol",
            "# FIXME: might break",
            "# HACK: temp workaround",
            "# NOTE: coffee needed",
            "# OPTIMIZE: someday"
        ]
        debug_ps = [
            'Write-Host "IDK if this works..."',
            'Write-Debug "Praying..."'
        ]
        debug_py = ['print("lol done-ish")', 'print("# sorry future me")']
        debug_js = ['console.log("Yeah... pray")', 'console.debug("hi mom")']

        debug_pool = {"PowerShell": debug_ps, "Python": debug_py, "JavaScript": debug_js}.get(lang, debug_ps)
        quirks = ["# hi mom", "# IDK why", "# lol what"]

        for i in range(len(new_lines)):
            if random.random() < 0.15:
                r = random.random()
                if r < 0.5:
                    new_lines.insert(i + 1, "    " + random.choice(markers))
                elif r < 0.8:
                    new_lines.insert(i + 1, "    " + random.choice(debug_pool))
                else:
                    new_lines.insert(i + 1, "    " + random.choice(quirks))
            if random.random() < 0.1:
                new_lines.insert(i + 1, "")

        # Style blending
        if style.strip():
            sample_lines = [l.strip() for l in style.splitlines() if l.strip()]
            if sample_lines:
                for _ in range(random.randint(1, 2)):
                    pos = random.randint(0, len(new_lines))
                    new_lines.insert(pos, random.choice(sample_lines))

        humanized = "\n".join(new_lines)

        # Watermark
        orig_hash = hashlib.sha256(code.encode('utf-8', errors='ignore')).hexdigest()[:16]
        watermark = f"# VATA-HUMANIZED: orig low → boosted | hash: {orig_hash} | review before prod"
        humanized += f"\n\n{watermark}"

        # Receipt
        receipt = json.dumps({
            "orig_hash": orig_hash,
            "orig_score": soul_score(code),
            "new_score": soul_score(humanized),
            "humanized": True
        }, indent=2)

        return humanized, watermark, receipt

    except Exception as e:
        return "Error during humanization", str(e), "{}"

with gr.Blocks(title="VATA Soul Check + Humanizer") as demo:
    gr.Markdown("# VATA – Enforce Human Soul in Code")
    gr.Markdown("Paste code → Run Humanize to score + add traceable chaos.")

    code_input = gr.Textbox(lines=12, label="Paste code here", placeholder="function Test { ... }")
    style_input = gr.Textbox(lines=5, label="Optional: Your style sample (blend chaos)", placeholder="# TODO: my style...")
    lang_input = gr.Dropdown(choices=["PowerShell", "Python", "JavaScript"], value="PowerShell", label="Language")

    result_box = gr.Textbox(label="Result (score info)", lines=3)
    humanized_box = gr.Textbox(label="Humanized Code", lines=12)
    receipt_box = gr.Textbox(label="Traceable Receipt (JSON)", lines=6)

    gr.Button("Run Humanize").click(
        fn=lambda code, style, lang: (
            f"Original score: {soul_score(code)}/100",
            humanize(code, lang, style)[0],
            humanize(code, lang, style)[2]
        ),
        inputs=[code_input, style_input, lang_input],
        outputs=[result_box, humanized_box, receipt_box]
    )

    gr.Markdown("Repo: https://github.com/LHMisme420/project-vata | @Lhmisme #ProjectVata")
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# One-time: generate or load your key pair (do this locally, never commit private key!)
# For testing: generate once and save public key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

def sign_receipt(receipt_dict):
    receipt_json = json.dumps(receipt_dict, sort_keys=True)
    signature = private_key.sign(
        receipt_json.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature.hex()

# In humanize function, after creating receipt:
receipt = {...}  # your existing dict
receipt["signature"] = sign_receipt(receipt)
receipt["signer_pubkey"] = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# Then return receipt as before
demo.launch()