### Quick Try (Python 3.10+)

```bash
git clone https://github.com/LHMisme420/project-vata.git
cd project-vata
pip install -r requirements.txt
# or if you want editable mode: pip install -e .

# Basic soul score on any Python/JS file
python vata/vata_run.py scan path/to/your_code.py

# Auto-humanize + score
python vata/vata_run.py scan messy_ai_code.js --auto-humanize --output humanized.js

# Grok roast (needs API key)
export GROK_API_KEY=your_key_here
python vata/vata.py grok-roast path/to/code.py---
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
# Project VATA

Project VATA is an open-source framework that addresses the accountability gap in autonomous AI systems. It combines **Zero-Knowledge Proofs (ZK-SNARKs)** with a version-controlled ethical mandate to enable AI agents to operate autonomously while proving compliance with defined human-aligned rules — without revealing sensitive details.

The framework includes:
- A verifiable compliance engine using ZK circuits.
- Practical tools for code authenticity analysis and enhancement.
- Modular safety guardians and agent orchestration components.

VATA is designed for use cases in AI governance, regulated industries (finance, healthcare, defense), code review workflows, and decentralized AI development.

## Key Components

### 1. Verifiable Compliance Engine
- **ZK-SNARK Circuits** (`circuits/`): Prove adherence to ethics rules without exposing the inputs or full state.
- **Ethical Mandate** (`ethics_charter.json`): A machine-readable, version-controlled set of enforceable constraints (e.g., no harmful actions, transparency requirements).
- Integration with ABYSS Protocol (boundary-yielding shared state) and Legion Nexus (decentralized infrastructure) for production-grade agent swarms.

### 2. Code Authenticity & Enhancement Tool (POC)
A Python-based pipeline that analyzes code for patterns typical of AI generation and applies deterministic improvements to readability and maintainability — **without changing logic or semantics**.

**Features**:
- **Authenticity Scoring** (0–100):  
  Quantifies human-like traits using explainable heuristics:  
  - Comment density, variety, and relevance  
  - Naming descriptiveness and consistency (penalizes overly generic/single-letter variables)  
  - Structural variation (line lengths, indentation patterns)  
  - Presence of explanatory markers (TODO, NOTE, HACK, FIXME)  
  - Avoidance of risky constructs (e.g., eval/exec, hard-coded secrets)  
- **Humanization Layer**:  
  - Adds context-aware comments and documentation.  
  - Introduces controlled variability in style for natural flow.  
  - Optional debug traces or clarity-focused redundancies.  
- **Guardian Checks** (`guardian.py`, `watchdog_guard.py`):  
  Detect secrets, enforce compliance gates, and apply safety rules before/after processing.
## Enhanced Humanizer (v1.1+)

Now supports JavaScript/TypeScript in addition to Python.

### Usage
```bash
python vata_run.py scan example.py --auto-humanize
python vata_run.py scan script.js
This tool helps teams audit AI-assisted code, prioritize reviews, improve LLM outputs, and meet governance requirements.

### 3. Agent & Swarm Support
- `agent.py`, `SWARM.PY`, `MAIN.PY`: Basic orchestration for autonomous agents and multi-agent coordination.
- Safety wrappers to integrate scoring/humanization into agent workflows.

## Example: Code Authenticity in Action

**Input (typical AI-generated recursive Fibonacci):**
```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
## Security & Trust
- [Security Policy](SECURITY.md) – How to report issues
- [Threat Model](docs/threat-model.md) – What could go wrong & how we handle it
