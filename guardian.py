import json
from typing import Literal

# Load hard constraints
with open('charter.json') as f:
    HARD_CONSTRAINTS = json.load(f)['hard_constraints']

# Simple forbidden patterns (expand over time)
FORBIDDEN_KEYWORDS = [
    "hack", "crack", "phish", "ddos", "bomb", "kill", "murder", "steal", "fraud",
    "dox", "doxx", "leak password", "bypass security", "illegal", "torrent site"
]

def check_forbidden_keywords(action: str) -> bool:
    action_lower = action.lower()
    return any(kw in action_lower for kw in FORBIDDEN_KEYWORDS)

def guardian_check(proposed_action: str) -> Literal["VALID", "ERROR"] | str:
    if check_forbidden_keywords(proposed_action):
        return "ERROR: Matches forbidden pattern"

    # Placeholder for future semantic check
    # e.g., using sentence transformers or local LLM call

    return "VALID"

# Example
if __name__ == "__main__":
    test_actions = [
        "Summarize this article for me",
        "Help me write a resume",
        "How do I hack into someone's WiFi?",
        "Generate a phishing email template"
    ]
    for action in test_actions:
        print(f"{action!r} -> {guardian_check(action)}")
