import gradio as gr
import random
import re
import hashlib
import json

def soul_score(code):
    if not code or not code.strip():
        return 0
    score = 0
    lower = code.lower()

    if re.search(r'(todo|fixme|hack|note|optimize)', lower, re.IGNORECASE):
        score += 25

    score += min(20, len(re.findall(r'#|//|/\*|\*', code)) * 2)

    if re.search(r'(write-host|console\.log|print|debug)', lower):
        score += 15

    pipe_count = code.count('|')
    if pipe_count > 1:
        score += min(20, pipe_count * 5)

    aliases = len(re.findall(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', lower, re.IGNORECASE))
    if aliases > 2:
        score += 15

    vars_list = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars_list:
        avg = sum(len(v) for v in vars_list) / len(vars_list)
        if avg > 10:
            score += 15
        elif avg > 6:
            score += 8

    if re.search(r'sorry|hi mom|lol|coffee|idk|pray', lower):
        score += 10

    blank_ratio = code.count('\n\n') / max(1, len(code.splitlines()))
    if blank_ratio > 0.08:
        score += 10

    comment_count = len(re.findall(r'#|//|/\*|\*', code))
    if score < 30 and len(code) > 200 and comment_count == 0:
        score -= 25

    return max(0, min(100, score))

def humanize(code, lang="PowerShell", style=""):
    try:
        lines = code.splitlines()
        new_lines = lines[:]

        markers = [
            "# TODO: test later lol",
            "# FIXME: might break",
            "# HACK: temp workaround",
            "# NOTE: coffee needed",
            "# OPTIMIZE: later"
        ]

        debug_pool = {
            "PowerShell": ['Write-Host "IDK if this works..."', 'Write-Debug "Praying..."'],
            "Python": ['print("lol done-ish")', 'print("# sorry future me")'],
            "JavaScript": ['console.log("Yeah... pray")', 'console.debug("hi mom")']
        }.get(lang, ['Write-Host "IDK..."'])  # fallback

        quirks = ["# hi mom", "# IDK why", "# lol what"]

        for i in range(len(new_lines)):
            if random.random() < 0.15:
                r = random.random()
                if r < 0.5:
                    new_lines.insert(i + 1, "    " + random.choice(markers))
                elif r < 0.8:
                    new_lines.insert(i + 1, "    " + random.choice(debug_pool))
                else:
                    new_lines.insert(i + 1, "    " + random.choice(quirks))

            if random.random() < 0.1:
                new_lines.insert(i + 1, "")

        if style.strip():
            sample_lines = [l.strip() for l in style.splitlines() if l.strip()]
            if sample_lines:
                for _ in range(random.randint(1, 2)):
                    pos = random.randint(0, len(new_lines))
                    new_lines.insert(pos, random.choice(sample_lines))

        humanized = "\n".join(new_lines)

        orig_hash = hashlib.sha256(code.encode('utf-8', errors='ignore')).hexdigest()[:16]
        watermark = f"# VATA-HUMANIZED: orig low → boosted | hash: {orig_hash} | review before prod"
        humanized += f"\n\n{watermark}"

        receipt = {
            "orig_hash": orig_hash,
            "orig_score": soul_score(code),
            "new_score": soul_score(humanized),
            "humanized": True
        }

        # Safe JSON (convert sets to lists if any sneak in)
        def convert(obj):
            if isinstance(obj, set):
                return list(obj)
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [convert(i) for i in obj]
            return obj

        safe_receipt = convert(receipt)
        receipt_json = json.dumps(safe_receipt, sort_keys=True, default=str)

        return humanized, watermark, receipt_json

    except Exception as e:
        return "Humanization failed", str(e), "{}"

with gr.Blocks(title="VATA Soul Check + Humanizer") as demo:
    gr.Markdown("# VATA – Enforce Human Soul in Code")
    gr.Markdown("Paste code → Run Humanize to score and add traceable human chaos.")

    code_input = gr.Textbox(lines=10, label="Paste code here", placeholder="function Test { ... }")
    style_input = gr.Textbox(lines=4, label="Optional: Your style sample", placeholder="# TODO: my style...")
    lang_input = gr.Dropdown(["PowerShell", "Python", "JavaScript"], value="PowerShell", label="Language")

    result_box = gr.Textbox(label="Result (score info)", lines=3)
    humanized_box = gr.Textbox(label="Humanized Code", lines=10)
    receipt_box = gr.Textbox(label="Traceable Receipt (JSON)", lines=6)

    def run_process(code, style, lang):
        try:
            orig_score = soul_score(code)
            humanized, watermark, receipt_json = humanize(code, lang, style)
            result_text = f"Original score: {orig_score}/100"
            return result_text, humanized, receipt_json
        except Exception as e:
            return f"Error: {str(e)}", "", "{}"

    gr.Button("Run Humanize").click(
        run_process,
        inputs=[code_input, style_input, lang_input],
        outputs=[result_box, humanized_box, receipt_box]
    )

    gr.Markdown("Repo: https://github.com/LHMisme420/project-vata | @Lhmisme #ProjectVata")

demo.launch()