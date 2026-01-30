# src/vata/humanizer.py
import random
import os

# Simple rule-based injections (expandable)
QUIRKY_COMMENTS = [
    "# TODO: fix this before prod lol",
    "# 3AM special - don't judge",
    "# send help this works but why",
    "# cursed but functional",
    "# debug print - remove me later",
    "# yeah... this is fine (copium)",
]

def inject_soul(code: str, intensity: float = 0.7) -> str:
    lines = code.splitlines()
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if random.random() < intensity * 0.15 and line.strip() and not line.strip().startswith('#'):
            # Inject after logical lines
            if random.random() < 0.4:
                new_lines.append("    " + random.choice(QUIRKY_COMMENTS))
            elif random.random() < 0.3:
                new_lines.append("    # wtf why does this even work")

    humanized = "\n".join(new_lines)

    # Optional: call Grok API for smarter rewrite (add your key/logic)
    if os.getenv("GROK_API_KEY"):
        # Placeholder – implement actual call
        pass

    return humanized
