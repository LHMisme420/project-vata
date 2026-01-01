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
