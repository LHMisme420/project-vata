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

    # NEGATION: Over-faking penalty (too many markers = suspicious)
    if markers > 8:
        overfake_penalty = min((markers - 8) * 8, 30)
        score -= overfake_penalty
        breakdown["Over-faking penalty (too many markers)"] = -overfake_penalty

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
            indent_points = min(int(variance(indents) * 4), 15)
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

        # PRODUCTION CODE BONUS (PowerShell)
        pro_bonus = 0
        if '[CmdletBinding()]' in code:
            pro_bonus += 10
        if re.search(r'try\s*{.*?}\s*catch', code, re.I | re.DOTALL):
            pro_bonus += 10
        if re.search(r'\[Parameter\(Mandatory\]', code):
            pro_bonus += 8
        if '-ErrorAction' in code:
            pro_bonus += 5
        if pro_bonus > 0:
            score += pro_bonus
            breakdown["Professional PS patterns"] = pro_bonus

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

    # NEGATION: Too much debug = suspicious
    if debug_points >= 10:  # maxed out
        overdebug_penalty = min((debug_points - 8) * 5, 15)
        score -= overdebug_penalty
        breakdown["Over-debug penalty"] = -overdebug_penalty

    score += debug_points
    breakdown["Debug/Logging"] = debug_points

    total = min(max(score, 0), 100)  # clamp to 0–100
    return {"total": total, "breakdown": breakdown, "language": lang}

def format_output(code):
    result = soul_score(code)
    total = result["total"]
    breakdown = result["breakdown"]

    verdict = (
        "🟢 Highly human / chaotic" if total >= 80 else
        "🟢 Definitely human" if total >= 60 else
        "🟡 Mixed / edited" if total >= 40 else
        "🔶 Likely AI / very clean"
    )

    bd_lines = [f"{k}: +{v}" if v > 0 else f"{k}: {v}" for k, v in breakdown.items() if k != "Language detected"]
    bd_text = "\n".join(bd_lines) or "No signals detected"

    suggestions = []
    if total < 60:
        suggestions.append("• Add some TODO/FIXME comments")
    if breakdown.get("Debug/Logging", 0) == 0:
        suggestions.append("• Add a debug print with personality")
    if breakdown.get("Aliases (PS)", 0) < 6:
        suggestions.append("• Use PowerShell aliases (? % gci cp)")
    if breakdown.get("Var name length", 0) < 10:
        suggestions.append("• Use longer/quirkier variable names")
    if not suggestions:
        suggestions.append("• Already strong human signal — keep it messy 😄")

    return (
        f"{total}/100",
        verdict,
        bd_text,
        "\n".join(suggestions)
    )

demo = gr.Interface(
    fn=format_output,
    inputs=gr.Textbox(lines=15, placeholder="Paste PowerShell, Python, JS code here..."),
    outputs=[
        gr.Textbox(label="Soul Score"),
        gr.Textbox(label="Verdict"),
        gr.Textbox(label="Breakdown"),
        gr.Textbox(label="Humanization Suggestions")
    ],
    title="Vata Soul Detector PoC",
    description="""Higher score = more human soul (comments, TODOs, debug, pipes/aliases, messiness).  
Professional patterns now rewarded. Over-faking penalized.  
Repo: https://github.com/LHMisme420/ProjectVata-PoC""",
    examples=[
        ["function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }"],
        ["# TODO: fix mess later\nfunction Chaos { gci . | % { Write-Host lol } }"]
    ]
)

demo.launch(server_name="0.0.0.0", server_port=7860)