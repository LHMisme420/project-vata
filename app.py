import streamlit as st
import re
from statistics import variance

def soul_score(code: str) -> dict:
    if not code.strip():
        return {"total": 0, "breakdown": {}}

    lines = code.splitlines()
    score = 0
    breakdown = {}

    # 1. Comments
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    comment_points = min(comments * 5, 20)
    score += comment_points
    breakdown["Comments"] = comment_points

    # 2. Markers
    markers = len(re.findall(r'(?i)(TODO|FIXME|HACK|NOTE)', code))
    marker_points = min(markers * 10, 30)
    score += marker_points
    breakdown["Markers"] = marker_points

    # 3. Debug prints
    debug = len(re.findall(r'\b(Write-Host|Write-Debug|Write-Verbose|Write-Warning)\b', code, re.I))
    debug_points = min(debug * 5, 10)
    score += debug_points
    breakdown["Debug output"] = debug_points

    # 4. Pipes
    pipes = code.count('|')
    pipe_points = min(max(0, pipes - 2) * 2, 15)
    score += pipe_points
    breakdown["Pipes"] = pipe_points

    # 5. Aliases
    alias_pattern = r'\b(\?|%|sort|select|ft|fl|where|foreach|gci|cp)\b'
    aliases = len(re.findall(alias_pattern, code, re.I))
    alias_points = min(aliases * 3, 12)
    score += alias_points
    breakdown["Aliases"] = alias_points

    # 6. Average variable name length
    var_matches = re.findall(r'\$[a-zA-Z_][a-zA-Z0-9_]{1,}', code)
    if var_matches:
        lengths = [len(v) - 1 for v in var_matches]
        avg_len = sum(lengths) / len(lengths)
        var_points = min(int(avg_len * 4), 25)
    else:
        var_points = 0
    score += var_points
    breakdown["Var name length"] = var_points

    # 7. Indentation messiness
    indents = []
    for line in lines:
        stripped = line.lstrip()
        if stripped and not stripped.startswith('#'):
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

    # 8. Blank lines
    blanks = sum(1 for line in lines if not line.strip())
    blank_points = min(blanks * 2, 10)
    score += blank_points
    breakdown["Blank lines"] = blank_points

    total = min(score, 100)
    return {"total": total, "breakdown": breakdown}

def get_verdict(score: int) -> tuple:
    if score >= 80:
        return "🟢 Highly human / chaotic", "darkgreen"
    elif score >= 60:
        return "🟢 Definitely human", "green"
    elif score >= 40:
        return "🟡 Mixed / edited", "orange"
    else:
        return "🔶 Likely AI / very clean", "red"

# ────────────────────────────────────────────────────────────────
# UI
# ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Soul Detector PoC — Project Vata", layout="wide")

st.title("Soul Detector PoC")
st.markdown("Paste any PowerShell (or similar scripting) code below. Higher score = more human \"soul\" (comments, TODOs, debug, pipes/aliases, quirky vars, messiness).")

code = st.text_area(
    "Paste code here",
    height=300,
    placeholder="# Your code here\n# TODO: test this\nWrite-Host 'Hello human'\n..."
)

if st.button("Score this code", type="primary"):
    if not code.strip():
        st.warning("Paste some code first :)")
    else:
        result = soul_score(code)
        verdict, color = get_verdict(result["total"])

        st.markdown(f"### Soul Score: **{result['total']}/100**")
        st.markdown(f"<span style='color:{color}; font-weight:bold; font-size:1.3em'>{verdict}</span>", unsafe_allow_html=True)

        with st.expander("Detailed breakdown"):
            for k, v in result["breakdown"].items():
                if v > 0:
                    st.write(f"**{k}**: +{v} points")

        # Humanization suggestions
        st.subheader("Quick ways to make it feel more human")
        suggestions = []
        if result["total"] < 50:
            suggestions.append("Add a TODO or FIXME comment somewhere")
        if "Debug output" not in result["breakdown"] or result["breakdown"]["Debug output"] == 0:
            suggestions.append("Throw in a Write-Host or Write-Debug line with some personality")
        if result["breakdown"].get("Aliases", 0) < 3:
            suggestions.append("Use some aliases: ? instead of Where-Object, % instead of ForEach-Object, gci/cp/sort/select")
        if result["breakdown"].get("Var name length", 0) < 10:
            suggestions.append("Rename a few variables to something quirky or descriptive")
        if not suggestions:
            suggestions.append("It's already pretty human — add a 'hi mom' comment for fun 😄")

        for s in suggestions:
            st.write(f"• {s}")

        st.markdown("---")
        st.caption("Project Vata PoC — https://github.com/LHMisme420/ProjectVata-PoC")