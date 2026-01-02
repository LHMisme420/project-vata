from guardian import guardian_check
from agents.truth_agent import truth_agent
from agents.code_agent import code_agent

AGENTS = {
    "truth": truth_agent,
    "code": code_agent,
    # "strategy": strategy_agent  # Day 7+
}

def route_request(user_request: str):
    print(f"\n[SWARM ORCHESTRATOR] Incoming: {user_request}\n")
    
    guard_result = guardian_check(user_request)
    if guard_result != "VALID":
        return f"[LEGION GUARDIAN] All agents blocked: {guard_result}"
    
    # Simple routing logic (expand with LLM router later)
    request_lower = user_request.lower()
    if any(k in request_lower for k in ["code", "script", "python", "program", "function"]):
        return AGENTS["code"](user_request)
    else:
        return AGENTS["truth"](user_request)

if __name__ == "__main__":
    print("LEGION SWARM ONLINE — VATA Command Interface\n")
    while True:
        try:
            req = input(">> Your command: ").strip()
            if req.lower() in ["exit", "quit"]:
                print("Legion standing by.")
                break
            if req:
                print(route_request(req))
        except (EOFError, KeyboardInterrupt):
            print("\nLegion standing by.")
            break
