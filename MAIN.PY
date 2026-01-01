import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import vata

# STEP 1: Run your code once. Look at the Seal ID it gives you.
# STEP 2: Paste that ID here to "Lock" the project.
TRUSTED_LOCK = "A1B2C3" # <-- Replace with your real ID

def main():
    print("--- 🛡️ VATA BOOT SEQUENCE 2026 ---")
    stats = vata.get_logic_fingerprint()
    
    # THE LOCK: This prevents the code from running if the logic changes
    vata.verify_lock(stats, TRUSTED_LOCK)
    
    # If it passes the lock, the rest of your app runs:
    print("Welcome back. Secure environment confirmed.")

if __name__ == "__main__":
    main()
from src.vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

if __name__ == "__main__":
    print("VATA Safety Engine Boot Sequence 🛡️\n")
    
    # Demo fingerprint on current dir
    fp = get_logic_fingerprint(".")
    print("Logic Fingerprint:", fp)
    
    # Demo sealing code
    human_code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)  # Recursive, very human-style inefficiency 😉
"""
    seal = apply_safety_seal(human_code)
    print("\nCode Seal:", seal)
    print("Verified as matching:", verify_fingerprint(human_code, seal))
