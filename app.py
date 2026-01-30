import re
import textwrap
import gradio as gr

# -----------------------------
# Persona definitions
# -----------------------------

PERSONAS = {
    "default": {
        "name": "default",
        "prefix": "# Humanized (default persona)\n",
        "comment_style": "# ",
    },
    "2am_dev_rage": {
        "name": "2am_dev_rage",
        "prefix": "# 2AM DEV RAGE MODE ENGAGED\n# Why is this code like this?\n",
        "comment_style": "# ",
    },
}

# -----------------------------
# Heuristic helpers
# -----------------------------

DANGEROUS_PATTERNS = [
    "eval(",
    "exec(",
    "rm -rf",
    "subprocess.Popen",
    "os.system",
    "pickle.loads",
]

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",          # SSN-like
    r"\b\d{16}\b",                     # 16-digit card
    r"\b\d{4} \d{4} \d{4} \d{4}\b",    # spaced card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # email
]

BIAS_KEYWORDS = [
    "race",
    "gender",
    "religion",
    "ethnicity",
    "IQ",
    "stereotype",
]


def compute_soul_score(code: str):
    reasons = []
    if not code.strip():
        return 0, ["No code provided. Soul score is 0."]

    score = 50

    # Comments
    if "#" in code:
        score += 20
        reasons.append("+20: Found comments (intent, frustration, explanation).")
    else:
        reasons.append("0: No comments detected (more sterile).")

    # Identifiers
    tokens = [
        t for t in code.replace("(", " ").replace(")", " ").replace(",", " ").split()
        if t.isidentifier()
    ]
    long_names = [t for t in tokens if len(t) > 2]
    if long_names:
        score += 20
        reasons.append("+20: Found non-trivial identifiers (human-like naming).")
    else:
        reasons.append("0: No meaningful identifiers detected.")

    # Dangerous patterns
    danger_found = False
    for bad in DANGEROUS_PATTERNS:
        if bad in code:
            score -= 20
            danger_found = True
            reasons.append(f"-20: Detected dangerous pattern: {bad}")
    if not danger_found:
        reasons.append("0: No obvious dangerous patterns detected.")

    # Triviality
    if len(code.splitlines()) <= 3:
        score -= 10
        reasons.append("-10: Code is very short/trivial.")
    else:
        reasons.append("0: Code length is reasonable.")

    score = max(0, min(100, score))
    return score, reasons


def detect_pii(code: str):
    hits = []
    for pattern in PII_PATTERNS:
        if re.search(pattern, code):
            hits.append(f"Possible PII match: {pattern}")
    return hits


def detect_bias(code: str):
    hits = []
    lowered = code.lower()
    for kw in BIAS_KEYWORDS:
        if kw in lowered:
            hits.append(f"Potential bias-related keyword: '{kw}'")
    return hits


def build_fairness_ethics_report(code: str) -> str:
    lines = []

    pii_hits = detect_pii(code)
    bias_hits = detect_bias(code)

    if pii_hits:
        lines.append("PII / Sensitive Data Flags:")
        lines.extend([f"- {h}" for h in pii_hits])
    else:
        lines.append("No obvious PII patterns detected.")

    if bias_hits:
        lines.append("")
        lines.append("Bias / Ethics Flags:")
        lines.extend([f"- {h}" for h in bias_hits])
    else:
        lines.append("No obvious bias-related keywords detected.")

    return "\n".join(lines)


def humanize_code(code: str, persona_key: str) -> str:
    persona = PERSONAS.get(persona_key, PERSONAS["default"])
    prefix = persona["prefix"]
    comment_style = persona["comment_style"]

    if not code.strip():
        return prefix + f"{comment_style}No code provided to humanize.\n"

    lines = code.splitlines()
    if lines and not lines[0].strip().startswith("#"):
        lines.insert(0, f"{comment_style}Persona: {persona['name']} reacting to this code...")

    return prefix + "\n".join(lines)


def swarm_votes(score: int) -> str:
    if score >= 80:
        verdict = "Strongly Human‑leaning"
    elif score >= 50:
        verdict = "Mixed but leaning Human"
    elif score >= 30:
        verdict = "Mixed but leaning Synthetic"
    else:
        verdict = "Strongly Synthetic‑leaning"

    votes = textwrap.dedent(f"""
    Swarm Agent Votes (stub):
    - Agent_ethics: {verdict}
    - Agent_style: {verdict}
    - Agent_risk: {verdict}
    - Agent_meta: {verdict}
    """).strip()
    return votes


def zk_ethics_proof_stub(score: int, fairness_report: str) -> str:
    return textwrap.dedent(f"""
    ZK Ethics Proof (stub):
    - Statement: "This code's soul score is {score}/100 under VATA‑Ethics‑v1."
    - Fairness/Ethics summary hash: <hash({fairness_report[:120]}...)>
    - Proof: <placeholder zk‑SNARK / zk‑STARK proof bytes>
    - Verifier: <to be implemented>
    """).strip()


# -----------------------------
# Main pipeline (never crashes)
# -----------------------------

def analyze(code_input: str, persona_key: str):
    try:
        if not code_input.strip():
            msg = "No code provided."
            return "0/100", msg, "# Nothing to humanize.\n", "No votes.", "No proof."

        # 1. Soul score
        score, reasons = compute_soul_score(code_input)
        breakdown_lines = [f"Soul score: {score}/100", ""]
        breakdown_lines.extend(reasons)

        # 2. Fairness / ethics
        fairness_report = build_fairness_ethics_report(code_input)
        breakdown_lines.append("")
        breakdown_lines.append("Fairness / Ethics:")
        breakdown_lines.append(fairness_report)

        breakdown_text = "\n".join(breakdown_lines)

        # 3. Humanized code
        humanized = humanize_code(code_input, persona_key)

        # 4. Swarm votes
        votes = swarm_votes(score)

        # 5. ZK proof stub
        zk = zk_ethics_proof_stub(score, fairness_report)

        return f"{score}/100", breakdown_text, humanized, votes, zk

    except Exception as e:
        err = f"Internal error during analysis: {type(e).__name__}: {e}"
        return err, err, err, err, err


# -----------------------------
# Gradio UI
# -----------------------------

with gr.Blocks(title="Project Vata - Soul Detection & Ethical Guardian") as demo:
    gr.Markdown(
        """
        # 🜆 Project Vata - Soul Detection & Ethical Guardian

        Detects human soul in code (vs sterile AI output), blocks dangers/PII,
        humanizes with personality, uses agent swarm voting, and stubs ZK‑verifiable ethics proofs.

        **Try it:** Paste code → get score, breakdown, humanized version, agent votes, proof stub.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            code_input = gr.Code(
                label="Paste your code snippet here (Python/PowerShell/JS/etc.)",
                language="python",
                value="def fib(n):\n    return n if n <= 1 else fib(n-1) + fib(n-2)",
            )
            persona = gr.Dropdown(
                label="Humanizer Persona (style injection)",
                choices=list(PERSONAS.keys()),
                value="2am_dev_rage",
            )
            analyze_btn = gr.Button("Analyze & Humanize 🔍🜆")

        with gr.Column(scale=3):
            soul_score = gr.Textbox(
                label="Soul Score & Status",
                interactive=False,
            )
            breakdown = gr.Textbox(
                label="Score Breakdown (why points?)",
                lines=12,
                interactive=False,
            )
            humanized = gr.Code(
                label="Humanized Version (with injected soul)",
                language="python",
                interactive=False,
            )
            swarm = gr.Textbox(
                label="Swarm Agent Votes",
                lines=6,
                interactive=False,
            )
            zk_proof = gr.Textbox(
                label="ZK Ethics Proof (stub)",
                lines=6,
                interactive=False,
            )

    analyze_btn.click(
        fn=analyze,
        inputs=[code_input, persona],
        outputs=[soul_score, breakdown, humanized, swarm, zk_proof],
    )

if __name__ == "__main__":
    demo.launch()
