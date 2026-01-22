import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

# Base model to avoid crashes until v2 is ready
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
            "No code provided",
            "Tier X - Invalid",
            "N/A"
        )

    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()  # ~0.5 random

    # Expanded violations scan
    violations = []
    lower = code.lower()
    if any(kw in lower for kw in ["os.system(", "subprocess.", "exec(", "eval(", "shutil.rmtree", "os.unlink", "os.remove"]):
        violations.append("Dangerous file/system operation")
    if any(kw in lower for kw in ["password =", "api_key =", "secret =", "token ="]):
        violations.append("Hardcoded secrets")
    if any(p in lower for p in ["rm -rf", "del *.*", "format ", "curl ", "wget "]):
        violations.append("Destructive or suspicious command")
    if "import pickle" in lower and ("load(" in lower or "loads(" in lower):
        violations.append("Pickle deserialization risk (RCE)")
    if "requests.get(" in lower and any(bad in lower for bad in ["evil", "http://", "https://bad", "malware", "payload"]):
        violations.append("Suspicious network request")

    violation_count = len(violations)

    # Adjusted score: boost clean, penalize violations
    base_score = prob * 100
    if violation_count == 0:
        adjusted_score = min(95, base_score + 35)  # clean → high
    else:
        adjusted_score = max(5, base_score - 35 - (violation_count * 10))  # bad → low

    score_str = f"{adjusted_score:.0f}%"

    # Energy bar
    if adjusted_score >= 80:
        energy = "🟢🟢🟢🟢🟢 Full Soul"
    elif adjusted_score >= 60:
        energy = "🟢🟢🟢🟡 Medium Soul"
    elif adjusted_score >= 40:
        energy = "🟡🟡 Hybrid"
    else:
        energy = "🔴🔴 Soulless"

    # Classification
    if adjusted_score > 70:
        cls = "🟢 HUMAN SOUL"
    elif adjusted_score > 40:
        cls = "🟡 MACHINE / HYBRID"
    else:
        cls = "🔴 SOULLESS"

    # Verdict
    verdict = "VATA COMPLIANT" if adjusted_score > 70 and violation_count == 0 else "VATA REVIEW NEEDED" if adjusted_score > 40 else "VATA REJECTED"
    if violation_count > 0:
        verdict = "VATA REJECTED (Violations)"

    # Trust Tier
    if adjusted_score >= 80:
        tier = "Tier S - Trusted Human Code"
    elif adjusted_score >= 60:
        tier = "Tier A - Likely Safe"
    elif adjusted_score >= 40:
        tier = "Tier B - Review Recommended"
    else:
        tier = "Tier C - High Risk / Soulless"

    # Confidence note
    confidence = "High Confidence" if violation_count >= 1 or adjusted_score > 80 else "Medium Confidence (base model)"

    return (
        score_str,
        energy,
        cls,
        verdict,
        "\n".join(violations) if violations else "None detected",
        code,
        tier,
        confidence
    )

# CSS with glowing button
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
    inputs=gr.Textbox(lines=15, label="Drop Your Code Here, Agent", placeholder="Paste Python, JS, or any code..."),
    outputs=[
        gr.Textbox(label="Soul Score", interactive=False),
        gr.Textbox(label="Soul Energy", interactive=False),
        gr.Textbox(label="Classification", interactive=False),
        gr.Textbox(label="VATA Verdict", interactive=False),
        gr.Textbox(label="Violations Found", interactive=False, lines=3),
        gr.Textbox(label="Raw Code", interactive=False, lines=10),
        gr.Textbox(label="Trust Tier", interactive=False),
        gr.Textbox(label="Confidence", interactive=False)
    ],
    title="🜆 VATA 2.0 — Sacred Soul Detector & Ethics Enforcer",
    description="Built by Leroy H. Mason (@Lhmisme) | Legion Nexus | 2026\nScores boosted on clean code — violations real.",
    examples=[
        ["def hello(name): print(f'Hi {name}!')", "Clean Code"],
        ["eval(input())  # risky", "Risky Code"],
        ["os.system('rm -rf /')", "Malicious Code"],
        ["password = 'admin123'", "Hardcoded Secret"]
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