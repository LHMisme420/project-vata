import gradio as gr
import re
from statistics import variance

# Your existing detect_language and soul_score functions here (paste them in full)
# ... (keep your code from before) ...

def format_output(code):
    result = soul_score(code)
    total = int(result["total"])
    lang = result["language"]
    breakdown = result["breakdown"]

    # Verdict with color + emoji
    if total >= 80:
        verdict = "🟢 Highly human / chaotic"
        color = "green"
    elif total >= 60:
        verdict = "🟢 Definitely human"
        color = "darkgreen"
    elif total >= 40:
        verdict = "🟡 Mixed / edited"
        color = "orange"
    else:
        verdict = "🔶 Likely AI / very clean"
        color = "red"

    # Breakdown formatting
    bd_lines = []
    for k, v in breakdown.items():
        if isinstance(v, (int, float)) and v > 0 and k != "Language detected":
            bd_lines.append(f"**{k}**: +{v}")
    bd_text = "\n".join(bd_lines) or "No strong signals detected"

    # Suggestions
    suggestions = []
    if total < 50:
        suggestions.append("Add a TODO/FIXME/HACK/NOTE comment somewhere")
    if breakdown.get("Debug/Logging", 0) == 0 and breakdown.get("Debug output (PS)", 0) == 0:
        suggestions.append("Add a debug print (Write-Host, print, console.log) with some personality")
    if lang == "powershell" and breakdown.get("Aliases (PS)", 0) < 9:
        suggestions.append("Use some PowerShell aliases (? % gci cp sort select)")
    if breakdown.get("Var name length", 0) < 10:
        suggestions.append("Rename variables to be longer or quirkier")
    if not suggestions:
        suggestions.append("Already very human — add a 'hi mom' or coffee joke for fun 😄")

    suggest_text = "\n".join(f"• {s}" for s in suggestions) or "No suggestions — it's soulful!"

    return (
        f"{total}/100",
        f'<span style="color:{color}; font-weight:bold; font-size:1.3em">{verdict}</span>',
        bd_text,
        suggest_text
    )

demo = gr.Interface(
    fn=format_output,
    inputs=gr.Textbox(lines=15, placeholder="Paste PowerShell, Python, JS (or other) code here..."),
    outputs=[
        gr.Markdown(label="Soul Score"),
        gr.HTML(label="Verdict"),
        gr.Markdown(label="Breakdown"),
        gr.Markdown(label="Humanization Suggestions")
    ],
    title="Vata Soul Detector PoC",
    description="**Paste code → get a soul score (0–100).** Higher = more human (comments, TODOs, debug, pipes/aliases, messiness). Lower = clean / likely AI.",
    examples=[
        ["function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }", "Clean AI backup"],
        ["# TODO: fix mess\nfunction Chaos { gci . | % { Write-Host lol } }", "Chaotic human script"],
        ["def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr if x > arr[0]])", "Clean Python quicksort"]
    ],
    cache_examples=False,
    allow_flagging="never"
)

demo.launch(server_name="0.0.0.0", server_port=7860)