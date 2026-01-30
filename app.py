# app.py ── Complete single-file VATA Simple Checker (no external deps except built-ins)
# Save this as app.py and run: streamlit run app.py
# Push to GitHub → Hugging Face Space will auto-detect and run it

import streamlit as st
import re
import math
import random

def simple_entropy(s: str) -> float:
    """Calculate Shannon entropy for variable names."""
    if not s:
        return 0.0
    counts = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    probs = [count / len(s) for count in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def score_soul(code: str) -> dict:
    """Main soul scoring function. Always returns a dict."""
    try:
        if not code.strip():
            return {
                "soul_score": 0,
                "category": "Empty Input",
                "signals": {"comments": 0, "todo_debug_quirky": 0, "name_entropy_avg": 0.0, "line_count": 0},
                "risks": ["No code provided"],
                "error": None
            }

        lines = [line for line in code.splitlines() if line.strip()]
        n_lines = max(1, len(lines))

        # Count signals
        comment_count = len(re.findall(r'#|//|/\*|\* ', code))
        todo_count    = len(re.findall(r'(?i)TODO|FIXME|HACK|NOTE', code))
        debug_count   = len(re.findall(r'(?i)print\s*\(|console\.log|dbg|debug', code))
        quirky_count  = len(re.findall(r'(?i)\b(lol|wtf|shit|crap|pls|pain|rip|send help|garbage|bruh|cursed)\b', code))

        var_names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', code)
        name_entropy = sum(simple_entropy(v) for v in var_names) / max(1, len(var_names)) if var_names else 0.0

        # Calculate score (tuned so messy code gets higher)
        score = 0
        score += min(35, comment_count * 3)
        score += min(30, (todo_count + debug_count + quirky_count) * 6)
        score += min(25, name_entropy * 10)
        score += min(30, min(1.0, n_lines / 10) * 30)

        score = int(min(100, max(0, score)))

        category = "Trusted Artisan 🔥" if score >= 70 else "Suspicious 👻" if score <= 40 else "Mixed ⚖️"

        risks = []
        if re.search(r'(?i)api_key|secret|token|password', code):
            risks.append("Possible secret / credential")
        if re.search(r'(?i)eval\(|exec\(', code):
            risks.append("Dangerous eval/exec")

        return {
            "soul_score": score,
            "category": category,
            "signals": {
                "comments": comment_count,
                "todo_debug_quirky": todo_count + debug_count + quirky_count,
                "name_entropy_avg": round(name_entropy, 2),
                "line_count": n_lines
            },
            "risks": risks,
            "error": None
        }

    except Exception as e:
        return {
            "soul_score": 0,
            "category": "Analysis Error",
            "signals": {},
            "risks": [],
            "error": str(e)
        }

def add_simple_soul(code: str) -> str:
    """Add random human-like comments."""
    try:
        lines = code.splitlines()
        injections = [
            "# TODO: fix later lol",
            "# 3am vibes don't judge",
            "# send help this works somehow",
            "# debug – remove before commit",
            "# cursed but cute 💀",
            "# yeah... this is fine (copium)",
        ]
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if random.random() < 0.18 and line.strip() and not line.strip().startswith('#'):
                new_lines.append("    " + random.choice(injections))
        return "\n".join(new_lines)
    except Exception as e:
        return code + f"\n\n# Humanizer failed: {str(e)}"

# ────────────────────────────────────────────────
#                Streamlit UI
# ────────────────────────────────────────────────

st.set_page_config(page_title="VATA Simple Checker", layout="wide")

st.title("🛡️ VATA Simple Checker")
st.markdown("Paste code → get soul score + optional humanization. Built by @Lhmisme")

code_input = st.text_area(
    "Paste your code here",
    height=300,
    placeholder="def example():\n    pass  # TODO: add some soul"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Analyze Soul", type="primary", use_container_width=True):
        result = score_soul(code_input)

        if result.get("error"):
            st.error(f"Analysis error: {result['error']}")
        else:
            color = "green" if result["soul_score"] >= 70 else "red" if result["soul_score"] <= 40 else "orange"
            st.markdown(f"<h2 style='color:{color}; text-align:center;'>{result['soul_score']}/100</h2>", unsafe_allow_html=True)
            st.markdown(f"**Category:** {result['category']}")

            with st.expander("Signals breakdown"):
                st.json(result["signals"])

            if result["risks"]:
                st.error("Risks detected: " + ", ".join(result["risks"]))

with col2:
    if st.button("Humanize (Add Soul)", use_container_width=True):
        humanized = add_simple_soul(code_input)
        st.code(humanized, language="python")

st.markdown("---")
st.caption("Project VATA – Verifiable AI Governance • Open Source • @Lhmisme • Reynolds, GA")
