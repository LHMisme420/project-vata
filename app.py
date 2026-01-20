def format_output(code):
    result = soul_score(code)
    total = int(result["total"])  # force to int here
    lang = result["language"]
    breakdown = result["breakdown"]

    verdict = (
        "🟢 Highly human / chaotic" if total >= 80 else
        "🟢 Definitely human" if total >= 60 else
        "🟡 Mixed / edited" if total >= 40 else
        "🔶 Likely AI / very clean"
    )

    bd_lines = [f"{k}: +{v}" for k, v in breakdown.items() if v > 0 and k != "Language detected"]
    bd_text = "\n".join(bd_lines) or "No strong signals detected"

    suggestions = []
    if total < 50:
        suggestions.append("Add a TODO/FIXME/HACK/NOTE comment")
    if breakdown.get("Debug/Logging", 0) == 0 and breakdown.get("Debug output (PS)", 0) == 0:
        suggestions.append("Add a debug print (print, console.log, Write-Host, etc.) with personality")
    if lang == "powershell" and breakdown.get("Aliases (PS)", 0) < 9:
        suggestions.append("Use some PowerShell aliases (? % gci cp sort select)")
    if breakdown.get("Var name length", 0) < 10:
        suggestions.append("Use longer or quirkier variable names")
    if not suggestions:
        suggestions.append("Already very human — add an easter egg comment for fun 😄")

    suggest_text = "\n".join(f"• {s}" for s in suggestions) or "No suggestions — it's soulful!"

    return (
        f"{total}/100",
        verdict,
        bd_text,
        suggest_text
    )

demo = gr.Interface(
    fn=format_output,
    inputs=gr.Textbox(lines=15, placeholder="Paste PowerShell, Python, JS (or other) code here..."),
    outputs=[
        gr.Textbox(label="Soul Score"),
        gr.Textbox(label="Verdict"),
        gr.Textbox(label="Breakdown"),
        gr.Textbox(label="Humanization Suggestions")
    ],
    title="Vata Soul Detector PoC",
    description="Higher score = more human soul (comments, markers, debug, pipes/aliases/chaining, messiness). Repo: https://github.com/LHMisme420/ProjectVata-PoC",
    examples=[
        ["function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }"],
        ["def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr if x > arr[0]])"],
        ["console.log('Hello'); const data = items.map(x => x * 2);"]
    ]
)

demo.launch(server_name="0.0.0.0", server_port=7860)