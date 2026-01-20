import gradio as gr
import random
import re
import hashlib
import json

# ── Soul Scoring Engine (your PoC heuristics, refined for speed) ──
def soul_score(code: str) -> int:
    if not code.strip():
        return 0
    score = 0
    lower = code.lower()
    # Compile regex once for efficiency
    comment_pat = re.compile(r'#|//|/\*|\*')
    marker_pat = re.compile(r'(todo|fixme|hack|note|optimize)', re.IGNORECASE)
    debug_pat = re.compile(r'(write-host|console\.log|print|debug|trace)', re.IGNORECASE)
    alias_pat = re.compile(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', re.IGNORECASE)

    if marker_pat.search(lower): score += 25
    score += min(20, len(comment_pat.findall(code)) * 2)
    if debug_pat.search(lower): score += 15

    pipe_count = code.count('|')
    if pipe_count > 1: score += min(20, pipe_count * 5)
    if len(alias_pat.findall(lower)) > 2: score += 15

    vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars:
        avg = sum(len(v) for v in vars) / len(vars)
        score += 15 if avg > 10 else 8 if avg > 6 else 0

    if re.search(r'sorry|hi mom|lol|coffee|idk|maybe|pray', lower):
        score += 10
    if code.count('\n\n') > len(code.splitlines()) * 0.08:
        score += 10

    # Clean AI penalty
    if score < 30 and len(code) > 200 and len(comment_pat.findall(code)) == 0:
        score -= 25

    return max(0, min(100, score))

# ── Revolutionary Humanizer: Injects soul + adds traceable watermark & receipt ──
def humanize_code(code: str, lang: str = "PowerShell", style_sample: str = "") -> tuple[str, str, str]:
    lines = code.splitlines()
    new_lines = lines[:]

    # Pools (your signature chaos)
    markers = [
        "# TODO: real test later lol",
        "# FIXME: breaks on big dirs – sorry",
        "# HACK: temp skip thumbs.db",
        "# NOTE: coffee run first",
        "# OPTIMIZE: maybe never"
    ]
    debug_ps = [
        'Write-Host "IDK if this survives prod..." -ForegroundColor DarkYellow',
        'Write-Debug "Praying this works..."'
    ]
    debug_py = ['print("lol done-ish # coffee time")', 'print("# sorry future me")']
    debug_js = ['console.log("Yeah... pray")', 'console.debug("hi mom")']

    debug_pool = {"PowerShell": debug_ps, "Python": debug_py, "JavaScript": debug_js}.get(lang, debug_ps)
    quirks = ["# hi mom don't judge", "# IDK why it works", "# lol what even is this"]

    insert_chance = 0.18

    for i in range(len(new_lines)):
        if random.random() < insert_chance:
            r = random.random()
            if r < 0.5: new_lines.insert(i + 1, f"    {random.choice(markers)}")
            elif r < 0.8: new_lines.insert(i + 1, f"    {random.choice(debug_pool)}")
            else: new_lines.insert(i + 1, f"    {random.choice(quirks)}")

        if random.random() < 0.12: new_lines.insert(i + 1, "")

    # Hybrid: blend from style sample
    if style_sample.strip():
        sample_lines = [l for l in style_sample.splitlines() if l.strip()]
        if sample_lines:
            for _ in range(random.randint(1, 3)):
                pos = random.randint(0, len(new_lines))
                new_lines.insert(pos, random.choice(sample_lines))

    humanized = "\n".join(new_lines)

    # Add revolutionary watermark
    orig_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
    water_mark = f"# VATA-HUMANIZED: orig soul low → boosted | orig hash: {orig_hash} | human review req before prod | #ProjectVata"
    humanized = f"{humanized}\n\n{water_mark}"

    # Receipt (for future ZK or audit)
    receipt = json.dumps({
        "original_hash": orig_hash,
        "original_score": soul_score(code),
        "humanized_score": soul_score(humanized),
        "timestamp": "2026-01-20T14:00:00Z",  # replace with real time later
        "humanizer_version": "v1-revolutionary"
    }, indent=2)

    return humanized, water_mark, receipt

# ── Gradio Interface ──
def process(code, style, lang, mode):
    if not code.strip():
        return "Paste code first!", "", "", ""

    orig_score = soul_score(code)

    if mode == "Score Only":
        verdict = "🔥 Peak chaos!" if orig_score >= 80 else "🟢 Solid human" if orig_score >= 60 else "🟡 Moderate" if orig_score >= 40 else "🔶 Likely AI slop"
        return f"Score: {orig_score}/100\n{verdict}", "", "", ""

    # Humanize mode
    humanized, watermark, receipt = humanize_code(code, lang, style)
    new_score = soul_score(humanized)
    boost = new_score - orig_score

    result = f"Original: {orig_score}/100 → Humanized: {new_score}/100 (+{boost})\nWatermark added:\n{watermark}"
    return result, humanized, receipt, ""

with gr.Blocks(title="VATA – Verifiable Human Texture") as demo:
    gr.Markdown("# Project VATA – Enforce Human Soul in Code")
    gr.Markdown("Detect AI slop. **Humanize** low-soul code with traceable chaos. Revolutionary provenance starts here.")

    code_input = gr.Textbox(lines=12, label="Paste code", placeholder="Your PS/JS/Python...")
    style_sample = gr.Textbox(lines=5, label="Optional: Style fingerprint (paste your own code to blend)", placeholder="Your chaotic snippets...")
    lang = gr.Dropdown(["PowerShell", "Python", "JavaScript"], value="PowerShell", label="Language")

    mode = gr.Radio(["Score Only", "Humanize + Trace"], value="Humanize + Trace", label="Mode")

    output_text = gr.Textbox(label="Result", lines=4)
    humanized_output = gr.Textbox(label="Humanized Code", lines=12)
    receipt_output = gr.Textbox(label="Traceable Receipt (for audit/ZK)", lines=6)

    gr.Button("Run").click(
        process,
        inputs=[code_input, style_sample, lang, mode],
        outputs=[output_text, humanized_output, receipt_output, gr.Textbox(visible=False)]
    )

    gr.Markdown("Repo: https://github.com/LHMisme420/project-vata & https://github.com/LHMisme420/ProjectVata-PoC | @Lhmisme #ProjectVata")

demo.launch()