import gradio as gr
import re
from statistics import variance
from random import choice, randint

def detect_language(code: str) -> str:
    code_lower = code.lower()
    if any(kw in code_lower for kw in ['write-host', 'param(', 'gci', 'cp ', '$']):
        return "powershell"
    if any(kw in code_lower for kw in ['def ', 'import ', 'print(', 'logger.']):
        return "python"
    if any(kw in code_lower for kw in ['console.log', 'function ', 'const ', 'let ', '=>']):
        return "javascript"
    return "generic"

def soul_score(code: str):
    if not code.strip():
        return {"total": 0, "breakdown": {}, "language": "empty"}

    lang = detect_language(code)
    lines = code.splitlines()
    score = 0
    breakdown = {"Language detected": lang}

    comments = sum(1 for line in lines if re.search(r'^\s*(#|//|/\*)', line.strip()))
    comment_points = min(comments * 5, 20)
    score += comment_points
    breakdown["Comments"] = comment_points

    markers = len(re.findall(r'(?i)\b(TODO|FIXME|HACK|NOTE|BUG|XXX)\b', code))
    marker_points = min(markers * 10, 30)
    score += marker_points
    breakdown["Markers"] = marker_points

    blanks = sum(1 for line in lines if not line.strip())
    blank_points = min(blanks * 2, 10)
    score += blank_points
    breakdown["Blank lines"] = blank_points

    indents = []
    for line in lines:
        stripped = line.lstrip()
        if stripped and not re.match(r'^\s*(#|//|/\*)', stripped):
            indents.append(len(line) - len(stripped))
    indent_points = 0
    if len(indents) > 3:
        try:
            var = variance(indents)
            indent_points = min(int(var * 4), 15)
        except:
            pass
    score += indent_points
    breakdown["Indent messiness"] = indent_points

    var_pattern = r'\b(?:[$@]?[a-zA-Z_][a-zA-Z0-9_]{1,})\b'
    vars_found = re.findall(var_pattern, code)
    var_points = 0
    if vars_found:
        lengths = [len(v) for v in vars_found if len(v) > 1]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            var_points = min(int(avg_len * 4), 25)
    score += var_points
    breakdown["Var name length"] = var_points

    debug_points = 0
    if lang == "powershell":
        pipes = code.count('|')
        pipe_points = min(max(0, pipes - 2) * 2, 15)
        score += pipe_points
        breakdown["Pipes (PS)"] = pipe_points

        alias_pattern = r'\b(\?|%|sort|select|ft|fl|where|foreach|gci|cp)\b'
        aliases = len(re.findall(alias_pattern, code, re.I))
        alias_points = min(aliases * 3, 12)
        score += alias_points
        breakdown["Aliases (PS)"] = alias_points

        debug = len(re.findall(r'\b(Write-Host|Write-Debug|Write-Verbose|Write-Warning)\b', code, re.I))
        debug_points = min(debug * 5, 10)

    elif lang == "python":
        debug = len(re.findall(r'\b(print|logger\.|logging\.|pdb\.|ipdb\.|console\.log)\b', code, re.I))
        debug_points = min(debug * 5, 10)

        comprehensions = len(re.findall(r'\[.* for .* in .*\]', code))
        comp_points = min(comprehensions * 3, 12)
        score += comp_points
        breakdown["List/set/dict comprehensions"] = comp_points

    elif lang == "javascript":
        debug = len(re.findall(r'\b(console\.log|console\.debug|debugger)\b', code, re.I))
        debug_points = min(debug * 5, 10)

        chains = len(re.findall(r'\.(then|catch|map|filter|forEach|reduce)\b', code, re.I))
        chain_points = min(chains * 2, 10)
        score += chain_points
        breakdown["Promise/Array chaining"] = chain_points

    if debug_points == 0:
        generic_debug = len(re.findall(r'\b(console\.log|print|log|debug|echo)\b', code, re.I))
        debug_points = min(generic_debug * 5, 10)

    score += debug_points
    breakdown["Debug/Logging"] = debug_points

    total = min(score, 100)
    return {"total": total, "breakdown": breakdown, "language": lang}

def format_output(code):
    if not code.strip():
        return "0/100", '<span style="color:red">🔶 Likely AI / very clean</span>', "Paste or upload code first", "No suggestions yet"

    result = soul_score(code)
    total = int(result["total"])
    breakdown = result["breakdown"]

    if total >= 80:
        verdict = '<span style="color:#2ecc71; font-weight:bold">🟢 Highly human / chaotic</span>'
    elif total >= 60:
        verdict = '<span style="color:#27ae60; font-weight:bold">🟢 Definitely human</span>'
    elif total >= 40:
        verdict = '<span style="color:#f39c12; font-weight:bold">🟡 Mixed / edited</span>'
    else:
        verdict = '<span style="color:#e74c3c; font-weight:bold">🔶 Likely AI / very clean</span>'

    bd_lines = []
    for k, v in breakdown.items():
        if isinstance(v, (int, float)) and v > 0 and k != "Language detected":
            bd_lines.append(f"<strong>{k}</strong>: +{v}")
    bd_text = "<br>".join(bd_lines) or "No strong signals detected"

    suggestions = []
    if total < 50:
        suggestions.append("Add a TODO/FIXME/HACK/NOTE comment somewhere")
    if breakdown.get("Debug/Logging", 0) == 0:
        suggestions.append("Throw in a debug print with some personality")
    if breakdown.get("Aliases (PS)", 0) < 9:
        suggestions.append("Use some PowerShell aliases (? % gci cp sort select)")
    if breakdown.get("Var name length", 0) < 10:
        suggestions.append("Rename variables to be longer or quirkier")
    if not suggestions:
        suggestions.append("Already very human — add an easter egg comment for fun 😄")

    suggest_text = "<br>".join(f"• {s}" for s in suggestions) or "No suggestions — it's soulful!"

    return (
        f"{total}/100",
        verdict,
        bd_text,
        suggest_text
    )

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Vata Soul Detector PoC")
    gr.Markdown("**Paste or upload code → get instant soul score (0–100)**")
    gr.Markdown("Higher = more human feel (comments, TODOs, debug, pipes/aliases, messiness, personality leaks). Lower = clean / likely AI-generated.")
    gr.Markdown("Repo: [github.com/LHMisme420/ProjectVata-PoC](https://github.com/LHMisme420/ProjectVata-PoC) • by @Lhmisme")

    with gr.Row():
        code_input = gr.Textbox(lines=12, placeholder="Paste PowerShell, Python, JS code here...", label="Code")
        file_input = gr.File(label="Or upload .ps1 / .py / .js file", file_types=[".ps1", ".py", ".js", ".cs", ".sh"])

    with gr.Row():
        score_btn = gr.Button("Score Code", variant="primary")
        clear_btn = gr.Button("Clear", variant="secondary")

    score_display = gr.Markdown(label="Soul Score", value="Waiting...")
    verdict_display = gr.Markdown(label="Verdict", value="")
    breakdown_display = gr.Markdown(label="Breakdown", value="")
    suggestions_display = gr.Markdown(label="Suggestions to Humanize", value="")

    why_expander = gr.Accordion("Why this score?", open=False)
    with why_expander:
        gr.Markdown("""
        - **Comments & markers** (TODO/FIXME/HACK/NOTE) = human planning & self-notes  
        - **Debug prints** (Write-Host, print, console.log) = human troubleshooting  
        - **Pipes/aliases/chaining** = natural scripting style  
        - **Var names & indentation mess** = human quirks & breathing room  
        - **Professional patterns** (CmdletBinding, try/catch) = experienced engineer  
        - **Penalties** for over-faking (too many markers/debug) = detects gaming
        """)

    def process_input(code, file):
        if file is not None:
            with open(file.name, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        return code

    def on_score(code, file):
        code = process_input(code, file)
        result = soul_score(code)
        total = int(result["total"])
        breakdown = result["breakdown"]

        verdict = (
            f'<span style="color:#2ecc71; font-weight:bold; font-size:1.4em">🟢 Highly human / chaotic ({total}/100)</span>' if total >= 80 else
            f'<span style="color:#27ae60; font-weight:bold; font-size:1.3em">🟢 Definitely human ({total}/100)</span>' if total >= 60 else
            f'<span style="color:#f39c12; font-weight:bold; font-size:1.2em">🟡 Mixed / edited ({total}/100)</span>' if total >= 40 else
            f'<span style="color:#e74c3c; font-weight:bold; font-size:1.2em">🔶 Likely AI / very clean ({total}/100)</span>'
        )

        bd_lines = [f"**{k}**: +{v}" for k, v in breakdown.items() if isinstance(v, (int, float)) and v > 0 and k != "Language detected"]
        bd_text = "<br>".join(bd_lines) or "No strong signals detected"

        suggestions = []
        if total < 50:
            suggestions.append("Add a TODO/FIXME/HACK/NOTE comment")
        if breakdown.get("Debug/Logging", 0) == 0:
            suggestions.append("Add a debug print with personality")
        if breakdown.get("Aliases (PS)", 0) < 9:
            suggestions.append("Use some PowerShell aliases (? % gci cp sort select)")
        if breakdown.get("Var name length", 0) < 10:
            suggestions.append("Use longer/quirkier variable names")
        if not suggestions:
            suggestions.append("Already very human — add an easter egg comment for fun 😄")

        suggest_text = "<br>".join(f"• {s}" for s in suggestions) or "No suggestions — it's soulful!"

        return f"**Soul Score: {total}/100**", verdict, bd_text, suggest_text

    score_btn.click(
        fn=on_score,
        inputs=[code_input, file_input],
        outputs=[score_display, verdict_display, breakdown_display, suggestions_display]
    )

    clear_btn.click(
        fn=lambda: ("", "", "", ""),
        outputs=[score_display, verdict_display, breakdown_display, suggestions_display]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)