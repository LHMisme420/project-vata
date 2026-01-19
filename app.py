import gradio as gr
import re
from statistics import variance

def detect_language(code: str) -> str:
    code_lower = code.lower()
    if any(kw in code_lower for kw in ['write-host', 'param(', 'gci', 'cp ', '$']):
        return "powershell"
    if any(kw in code_lower for kw in ['def ', 'import ', 'print(', 'logger.']):
        return "python"
    if any(kw in code_lower for kw in ['console.log', 'function ', 'const ', 'let ', '=>']):
        return "javascript"
    return "generic"

def soul_score(code: str) -> dict:
    if not code.strip():
        return {"total": 0, "breakdown": {}, "language": "empty"}

    lang = detect_language(code)
    lines = code.splitlines()
    score = 0
    breakdown = {"Language detected": lang}

    # Universal signals
    # Comments (language-agnostic: #, //, /* */)
    comments = sum(1 for line in lines if re.search(r'^\s*(#|//|/\*)', line.strip()))
    comment_points = min(comments * 5, 20)
    score += comment_points
    breakdown["Comments"] = comment_points

    # Markers (universal)
    markers = len(re.findall(r'(?i)\b(TODO|FIXME|HACK|NOTE|BUG|XXX)\b', code))
    marker_points = min(markers * 10, 30)
    score += marker_points
    breakdown["Markers"] = marker_points

    # Blank lines
    blanks = sum(1 for line in lines if not line.strip())
    blank_points = min(blanks * 2, 10)
    score += blank_points
    breakdown["Blank lines"] = blank_points

    # Indentation variance
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

    # Variable name length (generic regex for common langs)
    var_pattern = r'\b(?:[$@]?[a-zA-Z_][a-zA-Z0-9_]{1,})\b'  # $var, var, @var
    vars_found = re.findall(var_pattern, code)
    var_points = 0
    if vars_found:
        lengths = [len(v) for v in vars_found if len(v) > 1]
        if lengths:
            avg_len = sum(lengths) / len(lengths)
            var_points = min(int(avg_len * 4), 25)
    score += var_points
    breakdown["Var name length"] = var_points

    # Language-specific flavor
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

    # Generic debug fallback
    if debug_points == 0:
        generic_debug = len(re.findall(r'\b(console\.log|print|log|debug|echo)\b', code, re.I))
        debug_points = min(generic_debug * 5, 10)

    score += debug_points
    breakdown["Debug/Logging"] = debug_points

    total = min(score, 100)
    return {"total": total, "breakdown": breakdown, "language": lang}

# Gradio UI
demo = gr.Interface(
    fn=lambda code: (
        f"{soul_score(code)['total']}/100",
        "🟢 Highly human / chaotic" if soul_score(code)['total'] >= 80 else 
        "🟢 Definitely human" if soul_score(code)['total'] >= 60 else 
        "🟡 Mixed / edited" if soul_score(code)['total'] >= 40 else "🔶 Likely AI / very clean",
        "\n".join([f"{k}: +{v}" for k, v in soul_score(code)['breakdown'].items() if v > 0]),
        "It's already pretty human — add a 'hi mom' comment for fun 😄" if soul_score(code)['total'] >= 80 else
        "\n".join([
            "Add a TODO or FIXME comment",
            "Throw in a debug print with personality",
            "Use aliases/chaining" if "Aliases" in soul_score(code)['breakdown'] and soul_score(code)['breakdown']["Aliases"] < 9 else "",
            "Make variable names quirkier" if "Var name length" in soul_score(code)['breakdown'] and soul_score(code)['breakdown']["Var name length"] < 10 else ""
        ]).strip() or "No suggestions — it's soulful!"
    ),
    inputs=gr.Textbox(lines=15, placeholder="Paste code (PowerShell, Python, JS, etc.) here..."),
    outputs=[
        gr.Textbox(label="Soul Score"),
        gr.Textbox(label="Verdict"),
        gr.Textbox(label="Breakdown"),
        gr.Textbox(label="Humanization Suggestions")
    ],
    title="Vata Soul Detector PoC",
    description="Higher score = more human soul (comments, TODOs/FIXME/HACK/NOTE, debug, pipes/aliases/chaining, messiness). Repo: https://github.com/LHMisme420/ProjectVata-PoC",
    examples=[
        ["function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }"],
        ["def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr if x > arr[0]])"],
        ["console.log('Hello'); const data = items.map(x => x * 2);"]
    ],
    allow_flagging="never"
)

demo.launch()