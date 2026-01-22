# VATA Code Security Scanner

**Purpose**  
Static analysis tool that:
- Flags high-risk security patterns in code (Python, PowerShell, JS, etc.)
- Computes a stylistic complexity score based on observable features (comment density, debug artifacts, naming variability, etc.)

**Security-first priority** — rejects or warns on dangerous constructs.

**Current capabilities** (PoC level):
- Regex + keyword-based violation detection
- Basic heuristic scoring for style/provenance
- Optional CodeBERT integration (fallback if not loaded)

**Not intended claims**:
- No detection of "soul" or subjective human essence
- No cryptographic ZK proofs implemented yet
- Not production-ready; easily evadable with minor changes

**Live demo**  
https://huggingface.co/spaces/Lhmisme/vata-soul-check

**Repo background**  
Evolved from early experimentation; now refactored for clarity and security focus.

**Next steps planned**:
- Integrate Semgrep rules
- Fine-tune small classifier on human vs synthetic code datasets
- Add JSON output for CI/CD