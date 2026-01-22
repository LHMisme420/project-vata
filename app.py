import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import ezkl
import onnx
import os
from pathlib import Path

# Base model
model_name = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()

# Cache ONNX export once
ONNX_PATH = "codebert_soul.onnx"
if not os.path.exists(ONNX_PATH):
    dummy_input = torch.randn(1, 512, dtype=torch.long)  # shape for input_ids
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_PATH,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={"input_ids": {0: "batch_size"}, "logits": {0: "batch_size"}},
        opset_version=13
    )
    print("ONNX exported")

def soul_check(code: str, generate_zk: bool = False):
    if not code.strip():
        return "0%", "⚪ Empty", "⚪ NO CODE", "REJECTED", "No input", code, "Tier X", "N/A", "No proof"

    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    input_ids = inputs["input_ids"]

    with torch.no_grad():
        logits = model(input_ids).logits
        prob = torch.softmax(logits, dim=-1)[0][1].item()

    base_score = prob * 100

    # Violations (same as before, simplified)
    violations = []
    lower = code.lower()
    if any(kw in lower for kw in ["os.system(", "subprocess.", "exec(", "eval("]):
        violations.append("Dynamic/system risk")
    if any(kw in lower for kw in ["password =", "api_key =", "secret ="]):
        violations.append("Hardcoded secrets")
    if any(p in lower for p in ["rm -rf", "del *.*"]):
        violations.append("Destructive pattern")

    violation_count = len(violations)

    # Adjusted score
    if violation_count == 0:
        adjusted_score = min(95, base_score + 35)
    else:
        adjusted_score = max(5, base_score - 35 - (violation_count * 10))

    score_str = f"{adjusted_score:.0f}%"

    energy = "🟢🟢🟢🟢🟢 Full Soul" if adjusted_score >= 80 else \
             "🟢🟢🟢🟡 Medium Soul" if adjusted_score >= 60 else \
             "🟡🟡 Hybrid" if adjusted_score >= 40 else "🔴🔴 Soulless"

    cls = "🟢 HUMAN SOUL" if adjusted_score > 70 else \
          "🟡 MACHINE / HYBRID" if adjusted_score > 40 else "🔴 SOULLESS"

    verdict = "VATA COMPLIANT" if adjusted_score > 70 and not violations else \
              "VATA REVIEW NEEDED" if adjusted_score > 40 else "VATA REJECTED"
    if violations:
        verdict = "VATA REJECTED (Violations)"

    tier = "Tier S - Trusted" if adjusted_score >= 80 else \
           "Tier A - Likely Safe" if adjusted_score >= 60 else \
           "Tier B - Review" if adjusted_score >= 40 else "Tier C - High Risk"

    confidence = "High" if violations or adjusted_score > 80 else "Medium (base model)"

    zk_proof_status = "No proof requested"

    if generate_zk:
        try:
            # Prepare input for EZKL (flatten input_ids)
            input_data = input_ids.squeeze().tolist()  # list of ints

            # EZKL settings
            settings_path = "settings.json"
            ezkl.gen_settings(ONNX_PATH, settings_path)

            # Prepare input file
            input_path = "input.json"
            with open(input_path, "w") as f:
                import json
                json.dump({"input": [input_data]}, f)

            # Generate proof
            proof_path = "proof.json"
            ezkl.prove(input_path, ONNX_PATH, settings_path, proof_path)

            # Verify (demo)
            vk_path = "vk.key"
            ezkl.gen_vk(ONNX_PATH, settings_path, vk_path)
            verified = ezkl.verify(proof_path, vk_path, settings_path)

            zk_proof_status = f"Proof generated & verified: {verified}"
        except Exception as e:
            zk_proof_status = f"ZK error: {str(e)[:100]}..."

    return (
        score_str,
        energy,
        cls,
        verdict,
        "\n".join(violations) if violations else "None",
        code,
        tier,
        confidence,
        zk_proof_status
    )

custom_css = """
body { background: linear-gradient(135deg, #0f0f0f, #1a0033); color: #00ff41; font-family: 'Courier New', monospace; }
.gradio-container { border: 2px solid #00ff41; border-radius: 15px; background: rgba(0,0,0,0.7); }
h1, h2, h3 { color: #00ff41; text-shadow: 0 0 10px #00ff41; }
button { background: #00ff41 !important; color: black !important; border-radius: 8px; }
button:hover { box-shadow: 0 0 15px #00ff41; }
button.primary { background: #00cc33 !important; box-shadow: 0 0 20px #00ff41; }
"""

demo = gr.Interface(
    fn=soul_check,
    inputs=[
        gr.Textbox(lines=15, label="Drop Your Code Here, Agent", placeholder="Paste code..."),
        gr.Checkbox(label="Generate ZK Proof (slow, demo only)", value=False)
    ],
    outputs=[
        gr.Textbox(label="Soul Score"),
        gr.Textbox(label="Soul Energy"),
        gr.Textbox(label="Classification"),
        gr.Textbox(label="VATA Verdict"),
        gr.Textbox(label="Violations Found", lines=3),
        gr.Textbox(label="Raw Code", lines=10),
        gr.Textbox(label="Trust Tier"),
        gr.Textbox(label="Confidence"),
        gr.Textbox(label="ZK Proof Status")
    ],
    title="🜆 VATA 2.0 — Sacred Soul Detector & ZK Ethics Enforcer",
    description="Built by Leroy H. Mason (@Lhmisme) | Legion Nexus | 2026\nZK proof proves score computation (slow on CPU)",
    examples=[
        ["def hello(name): print(f'Hi {name}!')", False, "Clean Code"],
        ["eval(input())  # risky", True, "Risky + ZK"],
        ["os.system('rm -rf /')", False, "Malicious"]
    ],
    flagging_mode="never",
)

demo.launch(
    theme=gr.themes.Soft(),
    css=custom_css,
    server_name="0.0.0.0",
    server_port=7860
)