import sys
import os

# 1. TELL PYTHON WHERE THE 'SRC' IS
# This allows 'import vata' to work even without installing
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import vata

def main():
    # 2. RUN THE SAFETY CHECK BEFORE ANYTHING ELSE
    # This generates the "Geometric Seal" based on your local files
    print("\n--- 🛡️ VATA BOOT SEQUENCE 2026 ---")
    vata.run_safety_check()
    
    print("\n[SYSTEM STATUS]: ACTIVE")
    print("Welcome back. Your logic fingerprint is verified.")
    
    # 3. YOUR ACTUAL PROGRAM LOGIC GOES HERE
    print("\nReady for 2026 development. What are we building today?")

if __name__ == "__main__":
    main()
