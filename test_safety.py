import pytest
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

def test_human_code_scores_high():
    fp = get_logic_fingerprint(human_code)
    assert fp['human_score'] >= 70, f"Expected high human score, got {fp['human_score']}"

def test_ai_code_scores_low():
    fp = get_logic_fingerprint(ai_code)
    assert fp['human_score'] < 50, f"Expected low/AI score, got {fp['human_score']}"

def test_seal_and_verify():
    fp = get_logic_fingerprint(human_code)
    seal_data = apply_safety_seal(human_code, fp)
    verified, message = verify_fingerprint(human_code, seal_data)
    assert verified
    assert "HUMAN" in message
