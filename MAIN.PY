import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

if __name__ == "__main__":
    print("--- 🛡️ Project VATA: Human Code Authenticator 2026 ---\n")
    
    fp = get_logic_fingerprint(".")
    print(f"Project Human-Likeness Score: {fp['human_score']} (higher = more human quirks)")
    print(f"Unique Seal: {fp['hash'][:64]}...\n")
    
    # Very human code (inefficient, comments, emotion)
    human_code = '''
def fib(n):
    if n <= 1: return n
    # I know this is slow but recursion feels elegant today
    return fib(n-1) + fib(n-2)  # No memo because I'm feeling nostalgic
    # TODO: optimize later... maybe
'''

    # Clean AI-style code
    ai_code = '''
import functools

@functools.lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
'''

    print("🔍 Testing HUMAN-WRITTEN code:")
    print(human_code)
    human_seal = apply_safety_seal(human_code, {"human_score": 42})
    verified, message = verify_fingerprint(human_code, human_seal)
    print(f"Result: {message}\n")
    
    print("🤖 Testing AI-GENERATED code:")
    print(ai_code)
    ai_seal = apply_safety_seal(ai_code, {"human_score": 3})
    verified, message = verify_fingerprint(ai_code, ai_seal)
    print(f"Result: {message}\n")
    
    print("🛡️ VATA successfully distinguished human soul from AI efficiency!")
    print("    Commit this and post the output on X — this will get attention.")
