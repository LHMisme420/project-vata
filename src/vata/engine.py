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
import os

def calculate_soul_score(file_path):
    """Checks for 'Human' markers in the code."""
    score = 0
    if not os.path.exists(file_path):
        return 0
        
    with open(file_path, "r") as f:
        content = f.read()
        # Marker 1: TODOs (AI usually leaves these out unless prompted)
        if "TODO" in content or "FIXME" in content:
            score += 30
        # Marker 2: Personality/Human Slang
        if "bruh" in content or "crafty" in content.lower():
            score += 40
        # Marker 3: Structural Quarks (e.g., using specific print styles)
        if "---" in content:
            score += 30
            
    return min(score, 100)
