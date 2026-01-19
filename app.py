import gradio as gr

def greet(name):
    return "Hello " + name + "!!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()
st.markdown("""
### Try it!
Paste PowerShell code below. Higher score = more "human soul" (comments, TODOs, debug, mess, aliases, etc.).

**Example clean AI code (should score low):**
```powershell
function Backup { param($s, $d) Get-ChildItem $s | Copy-Item -Destination $d }