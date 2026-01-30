# Project VATA 🛡️🔥 – Verify Human Soul in Code

**VATA** detects AI-generated vs human-written code by scoring "soul" – messiness, personality, debug artifacts, entropy, behavioral patterns, provenance noise. Blocks risks, humanizes low-soul code with Grok-3.

### Soul Scores Explained
- **85–100** → **Trusted Artisan** 🔥 Full human soul
- **41–84** → **Mixed / Needs Review**
- **0–40** → **Suspicious / Soulless Void** 👻

### Quick Start
```bash
git clone https://github.com/LHMisme420/project-vata
cd project-vata
pip install -r requirements.txt

# CLI soul check
python vata.py your_code.py --model all-MiniLM-L6-v2 --behavioral

# Grok-powered roast & humanize (add your key!)
export GROK_API_KEY=your_key_here
python vata.py grok-roast your_code.py

# Web UI (local)
streamlit run app.py
