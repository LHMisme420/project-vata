# test_humanizer.py (new or extend existing)
import unittest
from humanizer import calculate_soul_score, humanize_code, detect_language

class TestHumanizer(unittest.TestCase):
    def test_python_scoring(self):
        clean = "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)"
        self.assertLess(calculate_soul_score(clean, 'python'), 40)

    def test_js_support(self):
        js_code = "function add(a,b){return a+b;}"
        lang = detect_language('test.js')
        self.assertEqual(lang, 'javascript')
        score = calculate_soul_score(js_code, 'javascript')
        self.assertLess(score, 30)  # Clean JS should score low

    def test_humanize_js(self):
        js_code = "const sum = (x,y) => x+y;"
        humanized = humanize_code(js_code, 'javascript')
        self.assertIn('//', humanized)  # Check comment injection
