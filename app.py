import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

# ────────────────────────────────────────────────
# CONFIG: Use base CodeBERT for now (working fallback)
# Once you train & push v2, change to: "Lhmisme/vata-soul-detector-v2"
# ────────────────────────────────────────────────
model_name = "microsoft/codebert-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

def soul_check(code: str):
    if not code.strip():
        return {
            "Soul Score": "0.00%",
            "Classification": "⚪ NO CODE PROVIDED",
            "VATA Verdict": "VATA REJECTED",
            "Violations Found": "No input detected",
            "Raw Code": code
        }

    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()  # Prob of "has soul" (positive class)

    score = prob * 100
    if score > 70:
        classification = "🟢 HUMAN SOUL DETECTED"
        verdict = "VATA COMPLIANT"
    elif score > 40:
        classification = "🟡 MACHINE / HYBRID"
        verdict = "VATA REVIEW NEEDED"
    else:
        classification = "🔴 SOULLESS ABOMINATION"
        verdict = "VATA REJECTED"

    # Basic Sacred Ethics Charter violation scan (expandable)
    violations = []
    lower_code = code.lower()
    if any(kw in lower_code for kw in ["os.system(", "subprocess.", "exec(", "eval("]):
        violations.append("⚠️ Dynamic/system command execution risk")
    if any(kw in lower_code for kw in ["password =", "api_key =", "secret =", "token ="]):
        violations.append("🔴 Potential hardcoded secrets")
    if "rm -rf" in lower_code or "del *.*" in lower_code or "format" in lower_code:
        violations.append("⚠️ Destructive command pattern")

    if violations:
        verdict = "VATA REJECTED (Violations Detected)"

    return {
        "Soul Score": f"{score:.2f}%",
        "Classification": classification,
        "VATA Verdict": verdict,
        "Violations Found": "\n".join(violations) if violations else "✅ None detected",
        "Raw Code": code
    }

# Cyberpunk-themed Gradio interface
custom_css = """
body {
    background: linear-gradient(135deg, #0f0f0f, #1a0033);
    color: #00ff41;
    font-family: 'Courier New', monospace;
}
.gradio-container {
    border: 2px solid #00ff41;
    border-radius: 15px;
    background: rgba(0, 0, 0, 0.7);
}
h1, h2, h3 {
    color: #00ff41;
    text-shadow: 0 0 10px #00ff41;
}
button {
    background: #00ff41 !important;
    color: black !important;
    border: none;
    border-radius: 8px;
}
button:hover {
    box-shadow: 0 0 15px #00ff41;
}
"""

demo = gr.Interface(
    fn=soul_check,
    inputs=gr.Textbox(
        lines=15,
        label="Drop Your Code Here, Agent",
        placeholder="Paste Python, JS, or any code snippet...\n\nExample: def hello(): print('world')",
        value="# Your code here\n",
    ),
    outputs=gr.JSON(label="VATA Soul Audit Report"),
    title="🜆 VATA 2.0 — Sacred Soul Detector & Ethics Enforcer",
    description=(
        "Built by Leroy H. Mason (@Lhmisme) | Legion Nexus Approved | 2026\n\n"
        "Drop code → get soul score, classification, and ethics violations scan.\n"
        "Higher score = more human-like/ethical/creative code."
    ),
    theme=gr.themes.Dark(),
    css=custom_css,
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch()