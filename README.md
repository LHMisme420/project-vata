# Project VATA — Verifiable AI Trust & Authenticity

**VATA** is an open-source toolkit designed to help developers, teams, and organizations distinguish human-authored code from AI-generated content in real-world codebases.

It analyzes source code using lightweight heuristics, embedding-based similarity checks, behavioral patterns, and structural signals to estimate the likelihood of **human origin** vs **AI generation**. The tool helps mitigate risks from low-quality AI output (shallow logic, missing error handling, insecure patterns) while preserving authentic developer style.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
![Status](https://img.shields.io/badge/status-alpha-orange)

## Why VATA?

As AI coding assistants become ubiquitous, repositories are increasingly filled with synthetic code that can introduce:
- Subtle bugs from incomplete reasoning
- Security anti-patterns (eval, shell injection risks)
- Maintenance debt (flat structure, missing comments/context)
- Provenance & IP uncertainty

VATA provides fast, local-first signals to:
- Flag probable AI-generated sections in PRs / audits
- Encourage human review of high-risk fragments
- Support future verifiable provenance (ZK-based human-origin proofs)

## Features (as of January 2026)

- **Local CLI checker** — paste or feed files, get instant origin score (0–100)
- **Embedding similarity** — compares against human vs AI reference centroids (using sentence-transformers)
- **Behavioral & structural signals**:
  - Comment density & personality markers
  - Control-flow / error-handling complexity
  - Identifier entropy & naming realism
  - Provenance noise (merge artifacts, commit-like strings)
  - Risk pattern detection (dangerous builtins, eval/exec, etc.)
- **Optional Grok-powered rewrite** — adds realistic human-style comments, structure, and safeguards (API key required)
- **Evasion resistance** — diminishing returns on naive "humanizing" tricks (fake TODO spam, random entropy)
- Supported languages: **Python**, **JavaScript/TypeScript**, **PowerShell** (more coming)

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
