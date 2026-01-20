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

def humanize_code(code):
    lines = code.splitlines()
    lang = detect_language(code)

    # Realistic human touches (language-aware)
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

    # Inject 3–6 random touches at random positions
    num_injects = randint(3, 6)
    for _ in range(num_injects):
        inject = choice(touches)
        insert_pos = randint(0, len(lines))
        lines.insert(insert_pos, inject)

    # Random variable rename (if vars exist)
    vars_found = re.findall(r'\b(?:[$@]?[a-zA-Z_][a-zA-Z0-9_]{1,})\b', code)
    if vars_found:
        old_var = choice(vars_found)
        new_var = choice([old_var + "_v2", old_var + "_quirky", old_var + "_temp", old_var + "_plswork"])
        code = code.replace(old_var, new_var, 1)  # replace one occurrence

    # Add random blank line
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

with gr.Blocks() as demo:
    gr.Markdown("# Vata Soul Detector PoC")
    gr.Markdown("Higher score = more human soul (comments, TODOs/FIXME/HACK/NOTE, debug, pipes/aliases, messiness). Lower = clean / likely AI.")
    gr.Markdown("Repo: https://github.com/LHMisme420/ProjectVata-PoC")

    code_input = gr.Textbox(lines=15, placeholder="Paste PowerShell, Python, JS code here...", label="Input Code")

    with gr.Row():
        score_btn = gr.Button("Score this code")
        humanize_btn = gr.Button("Humanize this code (make more human)")

    with gr.Row():
        score_out = gr.Textbox(label="Soul Score")
        verdict_out = gr.Textbox(label="Verdict")

    breakdown_out = gr.Textbox(label="Breakdown", lines=8)
    suggestions_out = gr.Textbox(label="Humanization Suggestions", lines=5)

    humanized_out = gr.Textbox(lines=15, label="Humanized Code (rescored after injection)")

    score_btn.click(
        fn=format_output,
        inputs=code_input,
        outputs=[score_out, verdict_out, breakdown_out, suggestions_out]
    )

    def humanize_and_rescore(code):
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

    humanize_btn.click(
        fn=humanize_and_rescore,
        inputs=code_input,
        outputs=[humanized_out, score_out]  # update humanized + rescore
    )

demo.launch(server_name="0.0.0.0", server_port=7860)