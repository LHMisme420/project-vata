import gradio as gr
import re
from statistics import variance

def soul_score(code):
    if not code.strip():
        return "0/100", "🔶 Likely AI / very clean", "Paste code first"

    lines = code.splitlines()
    score = 0
    breakdown = []

    # Comments
    comments = sum(1 for l in lines if l.strip().startswith('#'))
    comment_pts = min(comments * 5, 20)
    score += comment_pts
    breakdown.append(f"Comments: +{comment_pts}")

    # Markers
    markers = len(re.findall(r'(?i)(TODO|FIXME|HACK|NOTE)', code))
    marker_pts = min(markers * 10, 30)
    score += marker_pts
    breakdown.append(f"Markers: +{marker_pts}")

    # Debug
    debug = len(re.findall(r'\b(Write-Host|Write-Debug|Write-Verbose|Write-Warning)\b', code, re.I))
    debug_pts = min(debug * 5, 10)
    score += debug_pts
    breakdown.append(f"Debug output: +{debug_pts}")

    # Pipes
    pipes = code.count('|')
    pipe_pts = min(max(0, pipes - 2) * 2, 15)
    score += pipe_pts
    breakdown.append(f"Pipes: +{pipe_pts}")

    # Aliases
    alias_pattern = r'\b(\?|%|sort|select|ft|fl|where|foreach|gci|cp)\b'
    aliases = len(re.findall(alias_pattern, code, re.I))
    alias_pts = min(aliases * 3, 12)
    score += alias_pts
    breakdown.append(f"Aliases: +{alias_pts}")

    # Var length
    vars = re.findall(r'\$[a-zA-Z_][a-zA-Z0-9_]{1,}', code)
    var_pts = min(int((sum(len(v)-1 for v in vars) / len(vars) * 4) if vars else 0), 25)
    score += var_pts
    breakdown.append(f"Var name length: +{var_pts}")

    # Indent mess
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip() and not l.strip().startswith('#')]
    indent_pts = min(int(variance(indents)*4) if len(indents) > 3 else 0, 15)
    score += indent_pts
    breakdown.append(f"Indent messiness: +{indent_pts}")

    # Blanks
    blanks = sum(1 for l in lines if not l.strip())
    blank_pts = min(blanks * 2, 10)
    score += blank_pts
    breakdown.append(f"Blank lines: +{blank_pts}")

    total = min(score, 100)
    verdict = "🟢 Highly human / chaotic" if total >= 80 else "🟢 Definitely human" if total >= 60 else "🟡 Mixed / edited" if total >= 40 else "🔶 Likely AI / very clean"

    return f"{total}/100", verdict, "\n".join(breakdown)

iface = gr.Interface(
    fn=soul_score,
    inputs=gr.Textbox(lines=10, placeholder="Paste PowerShell code here..."),
    outputs=[gr.Textbox(label="Soul Score"), gr.Textbox(label="Verdict"), gr.Textbox(label="Breakdown")],
    title="Vata Soul Detector PoC",
    description="Higher score = more human soul (comments, TODOs, debug, pipes/aliases, messiness). Repo: https://github.com/LHMisme420/ProjectVata-PoC",
    examples=[
        ["function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }"],
        ["# TODO: fix mess\n# HACK: lol\ngci . | ? {$_} | % { cp $_ backup/ }\nWrite-Host 'Done? lol'"]
    ]
)

iface.launch()