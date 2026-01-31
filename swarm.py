# vata_swarm.py
# Project VATA - Swarm Architecture Demo
# Detects human soul in code using multiple specialized agents

from swarm import Swarm, Agent
import ast
import networkx as nx

# ============================
# CUSTOM FUNCTIONS FOR AGENTS
# ============================

def syntax_check(code: str):
    """Check if the code has valid Python syntax."""
    try:
        ast.parse(code)
        return {"status": "valid", "message": "Syntax is clean ✅"}
    except SyntaxError as e:
        return {"status": "invalid", "message": f"Syntax error: {str(e)} ❌"}

def fingerprint_analysis(code: str):
    """Build a simple logic fingerprint using AST and graph."""
    try:
        tree = ast.parse(code)
        G = nx.DiGraph()

        # Add nodes for functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                G.add_node(node.name, type="function")
            elif isinstance(node, ast.ClassDef):
                G.add_node(node.name, type="class")

        # Add edges for calls (simplified)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                caller = "root"
                callee = node.func.id
                G.add_edge(caller, callee)

        fingerprint_summary = {
            "nodes": list(G.nodes),
            "edges": list(G.edges),
            "complexity_score": len(G.nodes) + len(G.edges)
        }
        return {"fingerprint": fingerprint_summary, "message": "Fingerprint extracted 🧬"}
    except Exception as e:
        return {"error": str(e)}

def soul_scoring(fingerprint_data: dict):
    """Score the 'soul' based on complexity, uniqueness, and human-like messiness."""
    score = 0
    details = []

    complexity = fingerprint_data.get("complexity_score", 0)
    if complexity > 10:
        score += 30
        details.append("+30: Complex logic flow (human vibe)")
    elif complexity > 5:
        score += 15
        details.append("+15: Moderate complexity")

    node_count = len(fingerprint_data.get("nodes", []))
    if node_count > 3:
        score += 20
        details.append("+20: Multiple functions/classes")

    # Bonus for "root" edges (real control flow)
    if len(fingerprint_data.get("edges", [])) > 2:
        score += 20
        details.append("+20: Real function calls detected")

    final_score = min(score, 100)  # Cap at 100
    human_likelihood = "Strongly Human 🧑" if final_score >= 70 else "Likely AI 🤖" if final_score <= 40 else "Mixed 👀"

    return {
        "soul_score": final_score,
        "human_likelihood": human_likelihood,
        "breakdown": details
    }

def final_validation(results: list):
    """Validator agent aggregates everything and gives final verdict."""
    messages = [r.get("message", "") for r in results if "message" in r]
    soul = next((r for r in results if "soul_score" in r), None)

    verdict = soul["human_likelihood"] if soul else "Unknown"
    score = soul["soul_score"] if soul else 0

    return {
        "FINAL_VERDICT": verdict,
        "SOUL_SCORE": score,
        "summary": messages
    }

# ============================
# DEFINE THE AGENTS
# ============================

triage_agent = Agent(
    name="TriageAgent",
    instructions="You are the first guard. Check syntax. If invalid, stop and report. If valid, hand off to FingerprintAgent.",
    functions=[syntax_check]
)

fingerprint_agent = Agent(
    name="FingerprintAgent",
    instructions="You extract the unique logic fingerprint of the code. Always hand off to SoulScoringAgent after.",
    functions=[fingerprint_analysis]
)

soul_scoring_agent = Agent(
    name="SoulScoringAgent",
    instructions="You detect the soul. Score based on creativity, complexity, and human patterns. Hand off to ValidatorAgent.",
    functions=[soul_scoring]
)

validator_agent = Agent(
    name="ValidatorAgent",
    instructions="You are the final judge. Summarize all findings and give the official VATA verdict.",
    functions=[final_validation]
)

# ============================
# SETUP THE SWARM
# ============================

client = Swarm()

# ============================
# TEST FUNCTION - EASY TO RUN
# ============================

def verify_code_with_vata(code_snippet: str):
    print("🚀 PROJECT VATA SWARM ACTIVATED 🚀\n")
    print(f"Analyzing code:\n{code_snippet}\n{'-'*50}")

    response = client.run(
        agent=triage_agent,
        messages=[{"role": "user", "content": code_snippet}]
    )

    print("\n🔥 FINAL VATA VERDICT 🔥")
    print(response)

# ============================
# EXAMPLE USAGE - UNCOMMENT TO TEST
# ============================

if __name__ == "__main__":
    # Human-like code with soul
    human_code = """
# quick hack to process some junk data lol
def clean_data(stuff):
    result = []
    for item in stuff:
        if 'bad' not in item.lower():
            result.append(item.strip())
    return result

data = ["  good stuff  ", "BAD thing", " another good "]
print(clean_data(data))
"""

    # Clean AI-style code
    ai_code = """
def process_list(input_list):
    return [item.strip() for item in input_list if 'bad' not in item.lower()]
"""

    verify_code_with_vata(human_code)
    # verify_code_with_vata(ai_code)  # Uncomment to test AI code
