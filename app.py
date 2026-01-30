# app.py - Project VATA Web Interface (Streamlit)
import streamlit as st
import subprocess
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Project VATA 🛡️ - Verify Human Soul in Code",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for polish (clean, confident, breathing room) ---
st.markdown("""
    <style>
    .main { padding: 2rem 3rem; }
    .stButton>button { 
        background-color: #0D9488; color: white; border-radius: 8px; padding: 0.75rem 1.5rem; font-weight: bold;
    }
    .stTextArea>div>div>textarea { font-family: 'Courier New', monospace; font-size: 1.05rem; }
    .soul-score { font-size: 4rem; font-weight: bold; text-align: center; margin: 1rem 0; }
    .metric { font-size: 1.3rem; margin: 0.8rem 0; padding: 0.8rem; border-radius: 8px; background: #f1f5f9; }
    .high-soul { color: #10B981; }
    .low-soul { color: #EF4444; }
    .mixed-soul { color: #F59E0B; }
    section[data-testid="stSidebar"] { background: #0f172a; color: white; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("Project VATA 🛡️")
st.sidebar.markdown("**Verify Human Soul in Code**")
st.sidebar.markdown("Detect AI vs Human fingerprints • Inject personality • Block risks")
st.sidebar.markdown("---")
st.sidebar.info("Open-source • Launched Jan 2026 • By @Lhmisme")
st.sidebar.markdown("[GitHub Repo](https://github.com/LHMisme420/project-vata)")
st.sidebar.markdown("[Hugging Face Demo](https://huggingface.co/spaces/Lhmisme/vata-soul-check-humanizer)")  # update if needed

# Main area
st.title("VATA Soul Checker & Humanizer")
st.markdown("Paste code → get soul score, breakdown, humanization suggestions, risk flags. Clean layout, no distractions.")

# Split layout
col1, col2 = st.columns([3, 2])  # 60/40 feel

with col1:
    st.subheader("Your Code")
    code_input = st.text_area(
        label="Paste or type your code here...",
        height=500,
        placeholder="def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)  # TODO: make this less robotic",
        key="code_input"
    )
    
    lang = st.selectbox("Language (auto-detect fallback)", ["Python", "JavaScript", "PowerShell", "Other"], index=0)
    
    analyze_btn = st.button("Analyze Soul →", type="primary", use_container_width=True)

with col2:
    st.subheader("Results")
    result_container = st.empty()

if analyze_btn and code_input.strip():
    with st.spinner("Characterizing soul... 🧬"):
        # Save temp file for your CLI to process
        temp_path = Path("temp_input_code.py" if lang == "Python" else "temp_input_code")
        temp_path.write_text(code_input)
        
        try:
            # Call your existing vata.py CLI (adapt args as needed)
            # Example assuming vata.py accepts file + flags
            cmd = [
                "python", "vata/vata.py", str(temp_path),
                "--model", "all-MiniLM-L6-v2",
                "--behavioral",
                "--output", "json"   # ← add this flag to your CLI if not already
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                result_container.error(f"Analysis failed:\n{result.stderr}")
            else:
                try:
                    data = json.loads(result.stdout)
                    # Assume your JSON output has keys like: soul_score, category, metrics, risks, humanized_code, explanation
                    score = data.get("soul_score", 50)
                    category = data.get("category", "Mixed")
                    
                    color_class = "high-soul" if score >= 71 else "low-soul" if score <= 40 else "mixed-soul"
                    result_container.markdown(f'<div class="soul-score {color_class}">{score}/100</div>', unsafe_allow_html=True)
                    
                    if category == "Trusted Artisan":
                        result_container.success("**Full Soul Detected** 🔥 S+ Trusted Artisan")
                    elif category == "Suspicious":
                        result_container.error("**AI-like / Suspicious** 👻 Needs Human Touch")
                    else:
                        result_container.warning("**Mixed / Needs Review** ⚖️")
                    
                    # Breakdown
                    with result_container.expander("Soul Metrics Breakdown"):
                        for k, v in data.get("metrics", {}).items():
                            st.markdown(f'<div class="metric">{k}: **{v}**</div>', unsafe_allow_html=True)
                    
                    if "risks" in data and data["risks"]:
                        with result_container.expander("Risk Flags", expanded=True):
                            for risk in data["risks"]:
                                st.error(f"🚨 {risk}")
                    
                    if "humanized_code" in data:
                        with result_container.expander("Humanized Version (Inject Soul)"):
                            st.code(data["humanized_code"], language="python")
                            st.button("Copy Humanized", on_click=lambda: st.session_state.update(humanized=data["humanized_code"]))
                    
                    result_container.markdown(f"**Explanation**: {data.get('explanation', 'Behavioral + embedding analysis complete.')}")
                
                except json.JSONDecodeError:
                    result_container.info("Raw output:\n" + result.stdout)
        
        except Exception as e:
            result_container.error(f"Error during analysis: {str(e)}")
        
        finally:
            if temp_path.exists():
                temp_path.unlink()

# Quick examples section (friction reducer)
st.markdown("---")
st.subheader("Quick Try Examples")
example_col1, example_col2 = st.columns(2)
with example_col1:
    if st.button("Clean AI Factorial (low soul)"):
        st.session_state.code_input = """def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)"""
with example_col2:
    if st.button("Messy Human Chaos (high soul)"):
        st.session_state.code_input = """def factorial(n):  # TODO: fix recursion depth hell later
    if n == 0 or n == 1:  # base cases cuz im not tryna crash
        return 1
    result = 1
    for i in range(2, n+1):  # switched to loop cuz recursion is cursed at 3am
        result *= i
        print(f"dbg: {i} -> {result}")  # remove before prod lol
    return result  # send help"""

st.markdown("---")
st.caption("Project VATA – Verifiable AI Governance • Open Source • @Lhmisme")
