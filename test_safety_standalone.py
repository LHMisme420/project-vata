import pytest
import sys
sys.path.append('src')  # Force path

from vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

human_code = '''
def fib(n):
    if n <= 1: return n
    # I know this is slow but recursion feels elegant today
    return fib(n-1) + fib(n-2)
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

def test_human_high():
    fp = get_logic_fingerprint(human_code)
    print(f'Human score: {fp["human_score"]}')
    assert fp['human_score'] >= 60

def test_ai_low():
    fp = get_logic_fingerprint(ai_code)
    print(f'AI score: {fp["human_score"]}')
    assert fp['human_score'] < 60
