# test_humanizer_standalone.py - simple test runner

print("Starting humanizer test...")

try:
    from humanizer import VataHumanizer
    print("Imported VataHumanizer OK")
except ImportError as e:
    print("Import failed:", e)
    exit(1)

ai_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6))  # should print 720
"""

humanizer = VataHumanizer(chaos_level="rage", target_soul_score=70)

print("\nOriginal code:")
print(ai_code.strip())
print("-" * 60)

try:
    humanized = humanizer.humanize(ai_code)
    print("\nHumanized code:")
    print(humanized.strip())
    print("-" * 60)
    score = humanizer._get_soul_score(humanized)
    print(f"Soul score: {score}")
except Exception as e:
    print("Humanization crashed:")
    import traceback
    traceback.print_exc()
