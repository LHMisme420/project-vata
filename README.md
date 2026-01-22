---
title: VATA Code Security Scanner
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0   # Use your actual Gradio version; 4.0+ is fine, check requirements.txt
app_file: app.py
pinned: false
python_version: 3.10  # optional but recommended; match your env
---

# VATA Code Security Scanner

Scans code for common security risks (malicious patterns like eval/exec, destructive commands, hardcoded secrets)  
and computes a basic stylistic complexity score (higher values indicate more variable / commented / idiosyncratic style).

**Security check is primary** — flags high-risk constructs with line-level details.  
Stylistic score is heuristic only (comment density, debug prints, line variability, etc.) — not a reliable AI detector.

Experimental PoC — use for research / local testing, not production.

**Live app**: Paste code below to test.

Configuration reference: https://huggingface.co/docs/hub/spaces-config-reference