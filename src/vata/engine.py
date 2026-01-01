import sys

# Add this to your existing engine.py
def verify_lock(current_stats, trusted_id):
    """Checks if the current logic matches the human-verified lock."""
    import hashlib
    current_id = hashlib.sha256(current_stats["patterns"].encode()).hexdigest()[:6].upper()
    
    if current_id != trusted_id:
        print("\n" + "!"*45)
        print("CRITICAL SAFETY BREACH: LOGIC DRIFT DETECTED")
        print(f"EXPECTED ID: {trusted_id} | ACTUAL ID: {current_id}")
        print("TERMINATING PROCESS TO PREVENT UNSAFE EXECUTION")
        print("!"*45 + "\n")
        sys.exit(1) # This kills the program immediately
    else:
        print(f"[VATA]: Logic Verified. ID {current_id} matches Lock.")
