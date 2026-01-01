from .engine import get_logic_fingerprint
from .seal import create_seal

def run_safety_check():
    print("--- 2026 VATA SAFETY CHECK ---")
    data = get_logic_fingerprint()
    print(create_seal(data))

if __name__ == "__main__":
    run_safety_check()
