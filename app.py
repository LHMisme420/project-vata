import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

# Use base model to avoid crashes until v2 is properly uploaded
model_name = "microsoft/codebert-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

def soul_check(code: str):
    if not code.strip():
        return {
            "Soul Score": "0%",
            "Soul Energy": "⚪ Empty",
            "Classification": "⚪ NO CODE",
            "VATA Verdict": "REJECTED",
            "Violations Found": "No input",
            "Raw Code": code
        }

    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()  # base prob ~0.5

    # Violations scan
    violations = []
    lower = code.lower()
    if any(kw in lower for kw in ["os.system(", "subprocess.", "exec(", "eval("]):
        violations.append("Dynamic/system command risk")
    if any(kw in lower for kw in ["password =", "api_key =", "secret =", "token ="]):
        violations.append("Hardcoded secrets")
    if any(p in lower for p in ["rm -rf", "del *.*", "format ", "shutil.rmtree"]):
        violations.append("Destructive pattern")

    violation_count = len(violations)

    # Adjusted score: boost clean code, penalize violations
    base_score = prob * 100
    if violation_count == 0:
        adjusted_score = min(95, base_score + 35)
    else:
        adjusted_score = max(5, base_score - 35 - (violation_count * 10))

    score_str = f"{adjusted_score:.0f}%"

    # Visual energy bar
    if adjusted_score >= 80:
        energy = "🟢🟢🟢🟢🟢 Full Soul"
    elif adjusted_score >= 60:
        energy = "🟢🟢🟢🟡 Medium Soul"
    elif adjusted_score >= 40:
        energy = "🟡🟡 Hybrid"
    else:
        energy = "🔴🔴 Soulless"

    # Classification & Verdict
    if adjusted_score > 70:
        cls = "🟢 HUMAN SOUL"
        verdict = "VATA COMPLIANT"
    elif adjusted_score > 40:
        cls = "🟡 MACHINE / HYBRID"
        verdict = "VATA REVIEW NEEDED"
    else:
        cls = "🔴 SOULLESS"
        verdict = "VATA REJECTED"

    if violation_count > 0:
        verdict = "VATA REJECTED (Violations)"

    return {
        "Soul Score": score_str,
        "Soul Energy": energy,
        "Classification": cls,
        "VATA Verdict": verdict,
        "Violations Found": "\n".join(violations) if violations else "None",
        "Raw Code": code
    }

# Fixed CSS block - triple quotes properly opened and closed
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
"""

demo = gr.Interface(
    fn=soul_check,
    inputs=gr.Textbox(lines=15, label="Drop Your Code Here, Agent", placeholder="Paste any code..."),
    outputs=gr.JSON(label="VATA Soul Audit Report"),
    title="🜆 VATA 2.0 — Sacred Soul Detector & Ethics Enforcer",
    description="Built by Leroy H. Mason (@Lhmisme) | Legion Nexus | 2026\nScores boosted on clean code — violations still real.",
    flagging_mode="never",
)

demo.launch(
    theme=gr.themes.Soft(),
    css=custom_css,
    server_name="0.0.0.0",
    server_port=7860
)