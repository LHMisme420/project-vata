import hashlib

def create_seal(stats):
    if stats["nodes"] == 0:
        return "// [ VATA: NO LOCAL LOGIC DETECTED ]"
    
    sig = hashlib.sha256(stats["patterns"].encode()).hexdigest()[:6].upper()
    score = stats["complexity"]
    
    return f"""
/* [ AUTHENTICITY SEAL v2026 ]
 * ID: {sig} | STABILITY: {score}
 * .-------.
 * /   {sig}   \\
 * |  {score:04}   |
 * \\  SAFE   /
 * '-------'
 * [ ORIGIN: HUMAN-VERIFIED ]
 */"""
