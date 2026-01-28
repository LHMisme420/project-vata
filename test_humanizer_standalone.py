# test_humanizer_standalone.py

print("TEST START ───────────────────────────────────────")

try:
    from humanizer import VataHumanizer
    print("Import OK")
except Exception as e:
    print("Import failed:", e)
    exit(1)

code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6))  # should print 720
"""

print("\nOriginal:")
print(code.strip())
print("─" * 60)

humanizer = VataHumanizer(chaos_level="rage", target_soul_score=65)

try:
    result = humanizer.humanize(code)
    print("\nHumanized:")
    print(result.strip())
    print("─" * 60)
    print("Soul score:", humanizer._get_soul_score(result))
except Exception as e:
    print("Humanize failed:")
    import traceback
    traceback.print_exc()
