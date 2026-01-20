import gradio as gr
import random
import re

# Soul scoring (your PoC heuristics)
def soul_score(code: str) -> int:
    score = 0
    lower_code = code.lower()

    if re.search(r'(todo|fixme|hack|note|optimize)', lower_code, re.IGNORECASE):
        score += 25

    comment_count = len(re.findall(r'#|//|/\*|\*', code))
    score += min(20, comment_count * 2)

    if re.search(r'(write-host|console\.log|print|debug|trace)', lower_code):
        score += 15

    pipe_count = code.count('|')
    if pipe_count > 1:
        score += min(20, pipe_count * 5)
    alias_count = len(re.findall(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', lower_code, re.IGNORECASE))
    if alias_count > 2:
        score += 15

    vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars:
        avg_len = sum(len(v) for v in vars) / len(vars)
        if avg_len > 10:
            score += 15
        elif avg_len > 6:
            score += 8

    if re.search(r'sorry|hi mom|lol|coffee|idk|maybe|pray', lower_code):
        score += 10
    blank_lines = code.count('\n\n') + code.count('\r\n\r\n')
    if blank_lines > len(code.splitlines()) * 0.1:
        score += 10

    if score < 30 and len(code) > 200 and comment_count == 0:
        score -= 25

    return max(0, min(100, score))

# Humanizer
def humanize_code(code: str, lang: str = "PowerShell", style_sample: str = "") -> str:
    lines = code.splitlines()
    new_lines = lines[:]

    markers = [
        "# TODO: finish testing this mess",
        "# FIXME: Might break on large dirs lol",
        "# HACK: temporary workaround",
        "# NOTE: coffee break incoming",
        "# OPTIMIZE: yeah right",
    ]

    debug_prints = {
        "PowerShell": [
            'Write-Host "Backup complete? IDK check yourself!" -ForegroundColor Yellow',
            'Write-Debug "Pray this works..."',
        ],
        "Python": [
            'print("lol done-ish # coffee time")',
            'print("# sorry future me")',
        ],
        "JavaScript": [
            'console.log("Yeah probably works... pray")',
            'console.debug("hi mom check this")',
        ]
    }.get(lang, debug_prints["PowerShell"])

    quirks = ["# hi mom don't judge", "# IDK why this even works", "# lol what is this"]

    insert_chance = 0.18

    for i in range(len(new_lines)):
        if random.random() < insert_chance:
            choice = random.random()
            if choice < 0.5:
                marker = random.choice(markers)
                new_lines.insert(i + 1, f"    {marker}")
            elif choice < 0.8:
                new_lines.insert(i + 1, f"    {random.choice(debug_prints)}")
            else:
                new_lines.insert(i + 1, f"    {random.choice(quirks)}")

        if random.random() < 0.12:
            new_lines.insert(i + 1, "")

    if style_sample.strip():
        sample_lines = [l.strip() for l in style_sample.splitlines() if l.strip()]
        if sample_lines:
            for _ in range(random.randint(1, 3)):
                insert_pos = random.randint(0, len(new_lines))
                new_lines.insert(insert_pos, random.choice(sample_lines))

    humanized = "\n".join(new_lines)

    if soul_score(code) < 50 and random.random() < 0.4:
        humanized += f"\n\n    {random.choice(debug_prints)}  # VATA humanized this slop 🔥"

    return humanized

# Combined function for UI
def process(code_input, style_sample, lang):
    if not code_input.strip():
        return "Paste code first!", "", 0, ""

    original_score = soul_score(code_input)
    humanized_code = humanize_code(code_input, lang, style_sample)
    humanized_score = soul_score(humanized_code)

    score_text = f"Original: {original_score}/100\n"
    if original_score >= 80: score_text += "🔥 Peak human chaos!"
    elif original_score >= 60: score_text += "🟢 Solid human feel"
    elif original_score >= 40: score_text += "🟡 Moderate soul"
    else: score_text += "🔶 Low soul – likely AI"

    humanized_text = f"Humanized: {humanized_score}/100\n"
    if humanized_score > original_score:
        humanized_text += f"Boost: +{humanized_score - original_score} 🔥"
    else:
        humanized_text += "Already high soul!"

    return score_text, humanized_code, humanized_score, humanized_text

with gr.Blocks(title="VATA Soul Check + Humanizer") as demo:
    gr.Markdown("# Project VATA Soul Detector & Auto-Humanizer")
    gr.Markdown("Detect AI vs human code. **Humanize** low-soul input to add soul!")

    with gr.Row():
        code_input = gr.Textbox(label="Paste code", lines=12, placeholder="Your PowerShell/JS/Python...")
        style_sample = gr.Textbox(label="Optional: My style sample (blend your chaos)", lines=5)
        lang = gr.Dropdown(["PowerShell", "Python", "JavaScript"], value="PowerShell", label="Language")

    output_score = gr.Textbox(label="Score Breakdown")
    humanized_code = gr.Textbox(label="Humanized Output", lines=12)
    humanized_score = gr.Textbox(label="Humanized Score")

    with gr.Row():
        gr.Button("Score Only").click(process, inputs=[code_input, style_sample, lang], outputs=[output_score, gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False)])
        gr.Button("Humanize!").click(process, inputs=[code_input, style_sample, lang], outputs=[output_score, humanized_code, humanized_score, gr.Textbox(visible=False)])

    gr.Markdown("Repo: https://github.com/LHMisme420/ProjectVata-PoC | @Lhmisme #ProjectVata")

demo.launch()