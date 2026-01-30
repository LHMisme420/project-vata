# VATA — Visual Authorship & Transparency Analyzer  
Soul Scoring • Ethics Detection • Humanization • Fingerprinting • ZK‑Proof Stubs  
VATA is a multi‑dimensional code analysis engine designed to evaluate authorship signals, ethical risk, fairness and bias, human‑likeness, stylistic fingerprinting, explainability, and zero‑knowledge proof stubs. It runs fully offline, locally, and deterministically, providing a transparent and auditable analysis pipeline for developers, researchers, and compliance environments.

VATA includes soul scoring (0–100), ethics and fairness scanning, persona‑based humanization, swarm consensus voting, and a ZK‑Ethics proof stub. Upcoming modules include JSON output mode, batch folder scanning, and token‑level fingerprinting for authorship attribution.

The repository structure includes the CLI engine (`vata_cli.py`), JSON output module (`vata_json.py`), batch scanning engine (`vata_batch.py`), fingerprinting engine (`vata_fingerprint.py`), explainability hooks (`vata_explain.py`), Streamlit UI (`app.py`), fairness logic (`vata_fairness.py`), humanizer (`vatahumanizer.py`), legacy engine (`VATA.py`), tests, documentation, and this README.

The CLI is the primary interface for VATA. To analyze raw code, run:  
`python vata_cli.py analyze dummy --text "print('hello world')"`  
To analyze a file:  
`python vata_cli.py analyze myscript.py`  
To use a persona:  
`python vata_cli.py analyze dummy --text "print('x')" --persona 2am_dev_rage"`

Example output:  
==============================  
SOUL SCORE: 60/100  
==============================  
Breakdown:  
- 0: No comments detected.  
- +20: Found meaningful identifiers.  
- 0: No dangerous patterns detected.  
- -10: Code is very short/trivial.  
Fairness / Ethics:  
No PII detected.  
No bias-related keywords detected.  
Humanized Version:  
# Humanized (default persona)  
# Persona: default reacting...  
print('hello world')  
Swarm Votes:  
- Agent_ethics: Mixed but leaning Human  
- Agent_style: Mixed but leaning Human  
- Agent_risk: Mixed but leaning Human  
- Agent_meta: Mixed but leaning Human  
ZK Proof Stub:  
- Statement: "Soul score = 60/100 under VATA‑Ethics‑v1."  
- Fairness summary hash: <hash(...)>  
- Proof bytes: <placeholder>

JSON Mode (v2) will allow machine‑readable output using:  
`python vata_cli.py analyze dummy --text "print('hello')" --json`  
which returns structured JSON containing soul score, breakdown, fairness, humanized output, swarm votes, and ZK proof.

Batch folder scanning (v2) will allow repository‑wide analysis using:  
`python vata_cli.py analyze-folder C:\project`  
producing a JSON map of all analyzed files.

The fingerprinting engine (v2) will extract token distribution, identifier frequency, and stylistic signatures to support authorship attribution, drift detection, and compliance verification.

The roadmap includes real ZK‑proof generation, model‑agnostic drift cartography, governance and compliance capsules, full authorship lineage verification, API server mode, and a VSCode extension.

License: MIT (or your preferred license).
Early benchmarks show clean LLM output often scores <45 while real developer code (with quirks, debug aids, domain context) frequently reaches 70–95+.

## Installation

```bash
# Recommended: use a virtual environment
git clone https://github.com/LHMisme420/project-vata.git
cd project-vata

python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# or .venv\Scripts\activate   # Windows

pip install -r requirements.txt
<img width="1920" height="1080" alt="Screenshot (284)" src="https://github.com/user-attachments/assets/bfdee100-1760-4400-9b4f-9b2f6d79ca33" />
<img width="1920" height="1080" alt="Screenshot (285)" src="https://github.com/user-attachments/assets/415c5c10-cd8a-445e-872a-3c7323d81d8a" />
