import os
import sys

# Add src to path so we can import vata as a package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

if __name__ == "__main__":
    print("--- 🛡️ VATA Safety Engine Boot Sequence 2026 ---\n")
    
    # Demo 1: Get logic fingerprint of the current project directory
    print("Scanning project for logic fingerprint...")
    fp = get_logic_fingerprint(".")
    print("Logic Fingerprint:")
    print(fp)
    print(f"\nFingerprint Hash: {fp.get('hash', 'N/A')}\n")
    
    # Demo 2: Seal and verify a sample piece of human-like code
    human_code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)  # Recursive – classic human inefficiency 😏
    # No memoization, because who needs optimization on New Year's Day?
"""
    print("Sample Human-Written Code:")
    print(human_code)
    
    seal = apply_safety_seal(human_code)
    print(f"\nGenerated Safety Seal: {seal}")
    
    verified = verify_fingerprint(human_code, seal)
    print(f"Verification Result: {'🟢 HUMAN CODE CONFIRMED' if verified else '🔴 TAMPERED OR AI-GENERATED'}")
    
    print("\n🛡️ VATA demo complete – human logic sealed and verified!")
