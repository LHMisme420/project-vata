---
title: Vata Soul Check
emoji: 👀
colorFrom: purple
colorTo: green
sdk: gradio
sdk_version: 6.3.0
app_file: app.py
pinned: false
license: mit
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
# Vata Soul Detector PoC

Live demo: paste PowerShell code → get "human soul" score (0–100).

- Higher = more comments, TODOs/FIXME/HACK/NOTE, debug prints, pipes/aliases, messy vars/indentation.
- Lower = clean/minimal, likely AI-generated.

Repo: https://github.com/LHMisme420/ProjectVata-PoC

Try chaotic human code for 95+ scores!
## Live Demo (try in seconds!)
Paste any PowerShell, Python, JS (or other) code → instant soul score + breakdown + suggestions  
👉 https://huggingface.co/spaces/Lhmisme/vata-soul-check

Examples:
- Clean AI code → ~20–30/100 (Likely AI)
- Chaotic human code → 95–99/100 (Highly human)
