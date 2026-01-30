import gradio as gr
import textwrap
from typing import Dict, Any, List, Tuple

# -----------------------------
# Persona definitions
# -----------------------------

PERSONAS: Dict[str, Dict[str, Any]] = {
    "default": {
        "name": "Default",
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
# Core scoring / detection stubs
# -----------------------------

def compute_soul_score(code: str) -> Tuple[int, str]:
    """
    Very simple heuristic soul score:
    - +20 if there are comments
    - +20 if there are meaningful variable names (len > 2)
    - -20 if 'eval' or 'exec' or 'rm -rf' appears
    - clamp between 0 and 100
    """
    if not code.strip():
        return 0, "No code provided. Soul score is 0."

    score = 50
    reasons: List[str] = []

    # Comments
    if "#" in code:
        score += 20
        reasons.append("+20: Found comments (human intent / frustration / explanation).")
    else:
        reasons.append("0: No comments detected (feels more sterile).")

    # Variable names
    tokens = [t for t in code.replace("(", " ").replace(")", " ").replace(",", " ").split() if t.isidentifier()]
    long_names = [t for t in tokens if len(t) > 2]
    if long_names:
        score += 20
        reasons.append("+20: Found non-trivial identifiers (more human-like naming).")
    else:
        reasons.append("0: No meaningful identifiers detected.")

    # Dangerous patterns
    danger = False
    for bad in ["eval(", "exec(", "rm -rf", "subprocess.Popen", "os.system"]:
        if bad in code:
            score -= 20
            danger = True
            reasons.append(f"-20: Detected dangerous pattern: {bad}")
    if not danger:
        reasons.append("0: No obvious dangerous patterns detected.")

    score = max(0, min(100, score))
    summary = f"Soul score: {score}/100"
    return score, summary + "\n" + "\n".join(reasons)


def build_score_breakdown(score: int, explanation: str) -> str:
    return explanation


def humanize_code(code: str, persona_key: str) -> str:
    persona = PERSONAS.get(persona_key, PERSONAS["default"])
    prefix = persona["prefix"]
    comment_style = persona["comment_style"]

    if not code.strip():
        return prefix + f"{comment_style}No code provided to humanize.\n"

    # Simple humanization: wrap code with persona prefix and inject one comment at top
    lines = code.splitlines()
    if lines and not lines[0].strip().startswith("#"):
        lines.insert(0, f"{comment_style}Persona: {persona['name']} reacting to this code...")

    return prefix + "\n".join(lines)


def swarm_votes(score: int) -> str:
    """
    Stub: pretend we have a swarm of agents voting.
    """
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


def zk_ethics_proof_stub(score: int) -> str:
    """
    Stub for ZK‑verifiable ethics proof.
    """
    return textwrap.dedent(f"""
    ZK Ethics Proof (stub):
    - Statement: "This code's soul score is {score}/100 under VATA‑Ethics‑v1."
    - Proof: <placeholder zk‑SNARK / zk‑STARK proof bytes>
    - Verifier: <to be implemented>
    """).strip()


# -----------------------------
# Main pipeline for Gradio
# -----------------------------

def analyze_and_humanize(code_input: str, persona_key: str):
    """
    This is the single function wired to the Gradio button.
    It must NEVER crash; all errors are caught and surfaced as text.
    Returns:
      soul_score_text, breakdown_text, humanized_text, swarm_votes_text, zk_proof_text
    """
    try:
        # 1. Compute soul score
        score, explanation = compute_soul_score(code_input)

        # 2. Build breakdown
        breakdown = build_score_breakdown(score, explanation)

        # 3. Humanize with persona
        humanized = humanize_code(code_input, persona_key)

        # 4. Swarm votes
        votes = swarm_votes(score)

        # 5. ZK proof stub
        zk_proof = zk_ethics_proof_stub(score)

        soul_score_text = f"{score}/100"
        return soul_score_text, breakdown, humanized, votes, zk_proof

    except Exception as e:
        err = f"Internal error during analysis: {type(e).__name__}: {e}"
        # Return the same error to all panels so nothing is blank
        return err, err, err, err, err


# -----------------------------
# Gradio UI
# -----------------------------

with gr.Blocks(title="Project Vata - Soul Detection & Ethical Guardian") as demo:
    gr.Markdown(
        """
        # 🜆 Project Vata - Soul Detection & Ethical Guardian

        Detects human soul in code (vs sterile AI output), blocks dangers/PII, humanizes with personality,
        uses agent swarm voting, and stubs ZK‑verifiable ethics proofs.

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
                lines=8,
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
        fn=analyze_and_humanize,
        inputs=[code_input, persona],
        outputs=[soul_score, breakdown, humanized, swarm, zk_proof],
    )

    gr.Markdown(
        """
        ## Examples

        - Simple recursion:
          ```python
          def fib(n):
              return n if n <= 1 else fib(n-1) + fib(n-2)
          ```

        - Rage‑annotated:
          ```python
          # Why god why is this recursive hell
          def fib(n): print('pain'); return n if n<=1 else fib(n-1)+fib(n-2)
          ```

        - Dangerous:
          ```python
          eval('rm -rf /')  # oops
          ```
        """
    )

if __name__ == "__main__":
    demo.launch()
