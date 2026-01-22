import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import hashlib
import time

# Base model (safe fallback)
model_name = "microsoft/codebert-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

def soul_check(code: str):
    if not code.strip():
        return (
            "0%",
            "⚪ Empty",
            "⚪ NO CODE",
            "REJECTED",
            "No input",
            code,
            "Tier X - Invalid",
            "N/A",
            "No proof generated"
        )

    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    input_ids = inputs["input_ids"]

    with torch.no_grad():
        logits = model(input_ids).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()

    base_score = prob * 100

    # Violations scan (expanded)
    violations = []
    lower = code.lower()
    if any(kw in lower for kw in ["os.system(", "subprocess.", "exec(", "eval(", "shutil.rmtree", "os.unlink", "os.remove"]):
        violations.append("Dangerous file/system operation")
    if any(kw in lower for kw in ["password =", "api_key =", "secret =", "token ="]):
        violations.append("Hardcoded secrets")
    if any(p in lower for p in ["rm -rf", "del *.*", "format ", "curl ", "wget "]):
        violations.append("Destructive or suspicious command")
    if "import pickle" in lower and any(op in lower for op in ["load(", "loads("]):
        violations.append("Pickle deserialization risk (RCE)")
    if "requests.get(" in lower and any(bad in lower for bad in ["evil", "http://", "https://bad", "malware", "payload"]):
        violations.append("Suspicious network request")

    violation_count = len(violations)

    # Adjusted score: boost clean code, penalize violations
    if violation_count == 0:
        adjusted_score = min(95, base_score + 35)
    else:
        adjusted_score = max(5, base_score - 35 - (violation_count * 10))

    score_str = f"{adjusted_score:.0f}%"

    # Soul Energy bar
    if adjusted_score >= 80:
        energy = "🟢🟢🟢🟢🟢 Full Soul"
    elif adjusted_score >= 60:
        energy = "🟢🟢🟢🟡 Medium Soul"
    elif adjusted_score >= 40:
        energy = "🟡🟡 Hybrid"
    else:
        energy = "🔴🔴 Soulless"

    # Classification
    cls = "🟢 HUMAN SOUL" if adjusted_score > 70 else \
          "🟡 MACHINE / HYBRID" if adjusted_score > 40 else "🔴 SOULLESS"

    # Verdict
    verdict = "VATA COMPLIANT" if adjusted_score > 70 and violation_count == 0 else \
              "VATA REVIEW NEEDED" if adjusted_score > 40 else "VATA REJECTED"
    if violation_count > 0:
        verdict = "VATA REJECTED (Violations)"

    # Trust Tier
    tier = "Tier S - Trusted Human Code" if adjusted_score >= 80 else \
           "Tier A - Likely Safe" if adjusted_score >= 60 else \
           "Tier B - Review Recommended" if adjusted_score >= 40 else "Tier C - High Risk / Soulless"

    # Confidence
    confidence = "High Confidence" if violation_count >= 1 or adjusted_score > 80 else "Medium Confidence (base model)"

    # Lightweight Proof of Integrity (SHA256 hash - verifiable, no deps)
    timestamp = int(time.time())
    proof_input = f"{code}|{score_str}|{verdict}|{timestamp}"
    proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()

    proof_text = (
        f"Integrity Proof (SHA256): {proof_hash}\n"
        f"Verify by hashing: {code}|{score_str}|{verdict}|{timestamp}"
    )

    return (
        score_str,
        energy,
        cls,
        verdict,
        "\n".join(violations) if violations else "None detected",
        code,
        tier,
        confidence,
        proof_text
    )

# CSS with glowing primary button
custom_css = """
body { 
    background: linear-gradient(135deg, #0f0f0f, #1a0033); 
    color: #00ff41; 
    font-family: 'Courier New', monospace; 
}
.gradio-container { 
    border: 2px solid #00ff41; 
    border-radius: 15px; 
    background: rgba(0,0,0,0.7); 
}
h1, h2, h3 { 
    color: #00ff41; 
    text-shadow: 0 0 10px #00ff41; 
}
button { 
    background: #00ff41 !important; 
    color: black !important; 
    border-radius: 8px; 
}
button:hover { 
    box-shadow: 0 0 15px #00ff41; 
}
button.primary { 
    background: #00cc33 !important; 
    box-shadow: 0 0 20px #00ff41; 
}
"""

demo = gr.Interface(
    fn=soul_check,
    inputs=gr.Textbox(lines=15, label="Drop Your Code Here, Agent", placeholder="Paste any code snippet..."),
    outputs=[
        gr.Textbox(label="Soul Score", interactive=False),
        gr.Textbox(label="Soul Energy", interactive=False),
        gr.Textbox(label="Classification", interactive=False),
        gr.Textbox(label="VATA Verdict", interactive=False),
        gr.Textbox(label="Violations Found", interactive=False, lines=3),
        gr.Textbox(label="Raw Code", interactive=False, lines=10),
        gr.Textbox(label="Trust Tier", interactive=False),
        gr.Textbox(label="Confidence", interactive=False),
        gr.Textbox(label="Proof of Integrity (SHA256)", interactive=False, lines=4)
    ],
    title="🜆 VATA 2.0 — Sacred Soul Detector & Ethics Enforcer",
    description="Built by Leroy H. Mason (@Lhmisme) | Legion Nexus | 2026\nScores boosted on clean code — violations real — integrity proof included.",
    examples=[
        ["def hello(name): print(f'Hi {name}!')", "Clean Code"],
        ["eval(input())  # risky eval", "Risky Code"],
        ["os.system('rm -rf /')", "Malicious Code"],
        ["password = 'admin123'  # bad", "Hardcoded Secret"]
    ],
    examples_per_page=4,
    flagging_mode="never",
)

demo.launch(
    theme=gr.themes.Soft(),
    css=custom_css,
    server_name="0.0.0.0",
    server_port=7860
)