import sys
sys.path.append('src')

from vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

human_code = '''
def fib(n):
    if n <= 1: return n
    # I know this is slow but recursion feels elegant today
    return fib(n-1) + fib(n-2)  # No memo because I'm feeling nostalgic
    # TODO: optimize later... maybe
'''

ai_code = '''
import functools

@functools.lru_cache(maxsize=None)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
'''

print("=== VATA SOUL TEST 2026 ===")
fp = get_logic_fingerprint(human_code)
print(f"HUMAN CODE: {fp['message']} (Score: {fp['human_score']})")

fp_ai = get_logic_fingerprint(ai_code)
print(f"AI CODE: {fp_ai['message']} (Score: {fp_ai['human_score']})")

seal = apply_safety_seal(human_code, fp)
verified, msg = verify_fingerprint(human_code, seal)
print(msg)
