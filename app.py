import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

# Load the fine-tuned soul detector (CodeBERT base)
model_name = "Lhmisme/vata-soul-detector-v2"  # we'll push this in a sec
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

def soul_check(code):
    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()  # Probability of "has soul"
    
    score = prob * 100
    classification = "🟢 HUMAN SOUL DETECTED" if score > 70 else "🟡 MACHINE / HYBRID" if score > 40 else "🔴 SOULLESS ABOMINATION"
    
    # Sacred Ethics Charter violations scan
    violations = []
    if "os.system" in code or "subprocess" in code:
        violations.append("⚠️ Potential system command execution")
    if "eval(" in code or "exec(" in code:
        violations.append("⚠️ Dynamic code execution risk")
    if any(x in code.lower() for x in ["password", "api_key", "secret"]):
        violations.append("🔴 Hardcoded secrets detected")
    
    verdict = "VATA COMPLIANT" if score > 70 and len(violations) == 0 else "VATA REJECTED"
    
    return {
        "Soul Score": f"{score:.2f}%",
        "Classification": classification,
        "VATA Verdict": verdict,
        "Violations Found": "\n".join(violations) if violations else "✅ None",
        "Raw Code": code
    }

# Cyberpunk AF interface
iface = gr.Interface(
    fn=soul_check,
    inputs=gr.Textbox(lines=15, label="Drop Code Here, Agent", placeholder="paste python, js, whatever..."),
    outputs=gr.JSON(label="VATA Soul Audit Report"),
    title="🜆 VATA 2.0 — Sacred Soul Detector + Ethics Enforcer",
    description="Built by Leroy H. Mason @Lhmisme | Legion Nexus Approved | 2026",
    theme=gr.themes.Dark(),
    css="""
    body { background: linear-gradient(135deg, #0f0f0f, #1a0033); }
    .gradio-container { border: 2px solid #00ff41; border-radius: 15px; }
    """
)

iface.launch()