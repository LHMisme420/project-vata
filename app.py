import gradio as gr
import random
import re
import hashlib
import json

def soul_score(code):
    if not code.strip(): return 0
    score = 0
    lower = code.lower()
    if re.search(r'(todo|fixme|hack|note|optimize)', lower, re.I): score += 25
    score += min(20, len(re.findall(r'#|//|/\*|\*', code)) * 2)
    if re.search(r'(write-host|console\.log|print|debug)', lower): score += 15
    if code.count('|') > 1: score += min(20, code.count('|') * 5)
    aliases = len(re.findall(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', lower, re.I))
    if aliases > 2: score += 15
    vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars:
        avg = sum(len(v) for v in vars) / len(vars)
        if avg > 10: score += 15
        elif avg > 6: score += 8
    if re.search(r'sorry|hi mom|lol|coffee|idk|pray', lower): score += 10
    if code.count('\n\n') > len(code.splitlines()) * 0.08: score += 10
    if score < 30 and len(code) > 200 and len(re.findall(r'#|//|/\*|\*', code)) == 0:
        score -= 25
    return max(0, min(100, score))

def humanize(code, lang="PowerShell", style=""):
    lines = code.splitlines()
    new_lines = lines[:]

    markers = ["# TODO: test later lol", "# FIXME: breaks sometimes", "# HACK: temp fix", "# NOTE: coffee first", "# OPTIMIZE: maybe never"]
    debug = {
        "PowerShell": ['Write-Host "IDK if this works..." -ForegroundColor Yellow', 'Write-Debug "Praying..."'],
        "Python": ['print("lol done # coffee")', 'print("# sorry future me")'],
        "JavaScript": ['console.log("Yeah... pray")', 'console.debug("hi mom")']
    }.get(lang, debug["PowerShell"])
    quirks = ["# hi mom", "# IDK why", "# lol what"]

    for i in range(len(new_lines)):
        if random.random() < 0.18:
            r = random.random()
            if r < 0.5: new_lines.insert(i+1, "    " + random.choice(markers))
            elif r < 0.8: new_lines.insert(i+1, "    " + random.choice(debug))
            else: new_lines.insert(i+1, "    " + random.choice(quirks))
        if random.random() < 0.12: new_lines.insert(i+1, "")

    if style.strip():
        sample = [l for l in style.splitlines() if l.strip()]
        if sample:
            for _ in range(random.randint(1,3)):
                pos = random.randint(0, len(new_lines))
                new_lines.insert(pos, random.choice(sample))

    result = "\n".join(new_lines)
    orig_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
    watermark = f"# VATA-HUMANIZED: orig low → boosted | hash: {orig_hash} | review before prod"
    result += f"\n\n{watermark}"

    receipt = json.dumps({
        "orig_hash": orig_hash,
        "orig_score": soul_score(code),
        "new_score": soul_score(result),
        "humanized": True
    }, indent=2)

    return result, watermark, receipt

with gr.Blocks(title="VATA Soul + Humanizer") as demo:
    gr.Markdown("# VATA – Enforce Human Soul in Code")
    gr.Markdown("Score code soul. **Humanize** low-score code with traceable proof.")

    code = gr.Textbox(lines=12, label="Paste code here")
    style = gr.Textbox(lines=5, label="Optional: Your style sample (paste your code to blend)")
    lang = gr.Dropdown(["PowerShell", "Python", "JavaScript"], value="PowerShell", label="Language")

    result = gr.Textbox(label="Result", lines=4)
    humanized = gr.Textbox(label="Humanized code", lines=12)
    receipt_box = gr.Textbox(label="Traceable receipt (JSON)", lines=6)

    gr.Button("Run Humanize").click(
        lambda c, s, l: (f"Original score: {soul_score(c)}/100", humanize(c, l, s)[0], humanize(c, l, s)[2]),
        inputs=[code, style, lang],
        outputs=[result, humanized, receipt_box]
    )

    gr.Markdown("Repo: https://github.com/LHMisme420/project-vata | @Lhmisme #ProjectVata")

demo.launch()