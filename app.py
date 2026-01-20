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

    # Universal signals
    comments = sum(1 for line in lines if re.search(r'^\s*(#|//|/\*)', line.strip()))
    comment_points = min(comments * 5, 20)
    score += comment_points
    breakdown["Comments"] = comment_points

    markers = len(re.findall(r'(?i)\b(TODO|FIXME|HACK|NOTE|BUG|XXX)\b', code))
    marker_points = min(markers * 10, 30)
    score += marker_points
    breakdown["Markers"] = marker_points

    # Negation: Over-faking penalty
    if markers > 8:
        over_marker_penalty = min((markers - 8) * 8, 30)
        score -= over_marker_penalty
        breakdown["Over-faking penalty (too many markers)"] = -over_marker_penalty

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

        # PRODUCTION CODE BONUS
        pro_bonus = 0
        if '[CmdletBinding()]' in code:
            pro_bonus += 12
        if re.search(r'try\s*{.*?}\s*catch', code, re.I | re.DOTALL):
            pro_bonus += 10
        if re.search(r'\[Parameter\(Mandatory=', code, re.I):
            pro_bonus += 8
        if '-ErrorAction' in code or '-EA' in code:
            pro_bonus += 6
        if re.search(r'function\s+[A-Z][a-zA-Z0-9]+-[A-Z][a-zA-Z0-9]+', code):
            pro_bonus += 5
        if pro_bonus > 0:
            score += pro_bonus
            breakdown["Professional PS patterns bonus"] = pro_bonus

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

    # Negation: Over-debug penalty
    if debug_points > 6:
        over_debug_penalty = min((debug_points - 6) * 5, 20)
        score -= over_debug_penalty
        breakdown["Over-debug penalty (too much logging)"] = -over_debug_penalty

    # Over-chaos cap
    if markers + debug_points > 20:
        chaos_cap = 85 + (markers + debug_points - 20) * -2
        score = min(score, chaos_cap)
        breakdown["Over-chaos cap"] = f"Capped at {chaos_cap} (extreme marker/debug combo)"

    score += debug_points
    breakdown["Debug/Logging"] = debug_points

    total = min(max(score, 0), 100)
    return {"total": total, "breakdown": breakdown, "language": lang}

def humanize_code(code):
    lines = code.splitlines()
    lang = detect_language(code)

    touches = [
        "# TODO: review this later when I have time",
        "# HACK: this is temporary but it works... for now",
        "# NOTE: not sure if this is the best way but whatever",
        "# P.S. hi future me, sorry for the mess",
        "# if you're reading this - send coffee",
        "Write-Host 'Debug: still alive...' -ForegroundColor Yellow" if lang == "powershell" else
        "print('Debug: still alive...')  # lol why am I printing this" if lang == "python" else
        "console.log('Debug: still alive...') // send help",
        " # extra blank line for breathing room",
        " # oops forgot to fix this"
    ]

    num_injects = randint(3, 6)
    for _ in range(num_injects):
        inject = choice(touches)
        insert_pos = randint(0, len(lines))
        lines.insert(insert_pos, inject)

    vars_found = re.findall(r'\b(?:[$@]?[a-zA-Z_][a-zA-Z0-9_]{1,})\b', code)
    if vars_found:
        old_var = choice(vars_found)
        new_var = choice([old_var + "_v2", old_var + "_quirky", old_var + "_temp", old_var + "_plswork"])
        code = code.replace(old_var, new_var, 1)

    if randint(0, 1):
        blank_pos = randint(0, len(lines))
        lines.insert(blank_pos, "")

    return "\n".join(lines)

def format_output(code):
    if not code.strip():
        return "0/100", "🔶 Likely AI / very clean", "Paste some code first", "No suggestions yet"

    result = soul_score(code)
    total = int(result["total"])
    breakdown = result["breakdown"]

    verdict = (
        "🟢 Highly human / chaotic" if total >= 80 else
        "🟢 Definitely human" if total >= 60 else
        "🟡 Mixed / edited" if total >= 40 else
        "🔶 Likely AI / very clean"
    )

    bd_lines = [f"{k}: +{v}" for k, v in breakdown.items() if isinstance(v, (int, float)) and v > 0 and k != "Language detected"]
    bd_text = "\n".join(bd_lines) or "No strong signals detected"

    suggestions = []
    if total < 50:
        suggestions.append("• Add a TODO/FIXME/HACK/NOTE comment")
    if breakdown.get("Debug/Logging", 0) == 0:
        suggestions.append("• Add a debug print with personality")
    if breakdown.get("Aliases (PS)", 0) < 9:
        suggestions.append("• Use some PowerShell aliases (? % gci cp sort select)")
    if breakdown.get("Var name length", 0) < 10:
        suggestions.append("• Use longer/quirkier variable names")
    if not suggestions:
        suggestions.append("• Already max soul — add 'hi mom' for fun 😄")

    return (
        f"{total}/100",
        verdict,
        bd_text,
        "\n".join(suggestions)
    )

def humanize_and_rescore(code):
    if not code.strip():
        return "Paste some code first", "No score yet"

    humanized = humanize_code(code)
    result = soul_score(humanized)
    total = int(result["total"])

    verdict = (
        "🟢 Highly human / chaotic" if total >= 80 else
        "🟢 Definitely human" if total >= 60 else
        "🟡 Mixed / edited" if total >= 40 else
        "🔶 Likely AI / very clean"
    )

    return humanized, f"{total}/100 ({verdict})"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Vata Soul Detector PoC")
    gr.Markdown("Higher score = more human soul (comments, TODOs/FIXME/HACK/NOTE, debug, pipes/aliases, messiness). Lower = clean / likely AI.")
    gr.Markdown("Repo: https://github.com/LHMisme420/ProjectVata-PoC")

    with gr.Row():
        code_input = gr.Textbox(lines=15, placeholder="Paste PowerShell, Python, JS code here...", label="Input Code")
        file_input = gr.File(label="Or upload .ps1 / .py / .js file", file_types=[".ps1", ".py", ".js", ".cs", ".sh"])

    with gr.Row():
        score_btn = gr.Button("Score this code", variant="primary")
        humanize_btn = gr.Button("Humanize this code (inject soul)")

    with gr.Row():
        score_out = gr.Textbox(label="Soul Score (Original)")
        verdict_out = gr.Textbox(label="Verdict (Original)")

    breakdown_out = gr.Textbox(label="Breakdown (Original)", lines=8)
    suggestions_out = gr.Textbox(label="Humanization Suggestions (Original)", lines=5)

    humanized_code = gr.Textbox(lines=15, label="Humanized Code")
    humanized_score = gr.Textbox(label="Soul Score (After Humanize)")

    def process_input(code, file):
        if file is not None:
            with open(file.name, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        return code

    score_btn.click(
        fn=process_input,
        inputs=[code_input, file_input],
        outputs=code_input
    ).then(
        fn=format_output,
        inputs=code_input,
        outputs=[score_out, verdict_out, breakdown_out, suggestions_out]
    )

    humanize_btn.click(
        fn=process_input,
        inputs=[code_input, file_input],
        outputs=code_input
    ).then(
        fn=humanize_code,
        inputs=code_input,
        outputs=humanized_code
    ).then(
        fn=format_output,
        inputs=humanized_code,
        outputs=[humanized_score, gr.Textbox(visible=False), gr.Textbox(visible=False), gr.Textbox(visible=False)]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)