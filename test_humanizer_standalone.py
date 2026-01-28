# test_humanizer_standalone.py - COMPLETE STANDALONE VERSION (Jan 28, 2026)
# This should run out-of-the-box once libcst is installed

print("=== VATA HUMANIZER TEST STARTED ===")
print("Script running in:", __file__)

try:
    from humanizer import VataHumanizer
    print("SUCCESS: Imported VataHumanizer from humanizer.py ✓")
except ImportError as e:
    print("IMPORT FAILED - check you're in the right folder")
    print("Error:", e)
    input("Press Enter to exit...")
    exit(1)

# === MOCK SOUL SCORER (safe fallback - comment out if using real one) ===
def mock_soul_score(code: str) -> int:
    comment_count = code.count("#") + code.count("//") + code.count("/*")
    length_bonus = len(code) // 20
    chaos_bonus = code.count("lol") * 5 + code.count("bruh") * 5 + code.count("wtf") * 5
    return min(95, 40 + comment_count * 8 + length_bonus + chaos_bonus)

# Monkey-patch the mock scorer (remove these lines if your real scorer works)
VataHumanizer._get_soul_score = staticmethod(mock_soul_score)
print("Using MOCK soul scorer (safe mode)")

# === EXAMPLE AI CODE TO HUMANIZE ===
ai_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6)) # should print 720
"""

print("\n=== ORIGINAL AI CODE ===")
print(ai_code.strip())
print("-" * 70)

# === CREATE HUMANIZER ===
try:
    humanizer = VataHumanizer(chaos_level="rage", target_soul_score=75)
    print("Humanizer created with rage mode + target 75 ✓")
except Exception as e:
    print("Failed to create VataHumanizer:")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
    exit(1)

# Optional: personalize if you want (uncomment and change username)
# humanizer.personalize_from_github("Lhmisme")

# === HUMANIZE ===
print("\nHumanizing... (this might take a sec if loop is slow)")
try:
    humanized = humanizer.humanize(ai_code)
    
    print("\n=== HUMANIZED CODE (rage mode) ===")
    print(humanized.strip())
    print("-" * 70)
    
    final_score = humanizer._get_soul_score(humanized)
    print(f"FINAL SOUL SCORE: {final_score}")
    
    if final_score >= 75:
        print("🔥 TARGET REACHED! This code has SOUL now king ⚡")
    else:
        print("Score a bit low - we can crank chaos higher or tweak transformations next")
    
except AttributeError as e:
    print("\nAttributeError during humanize - likely still missing something:")
    import traceback
    traceback.print_exc()
    print("\nQUICK FIX TIP: Add self.style_profile in ChaosTransformer.__init__ like this:")
    print("""
    self.style_profile = {
        "comment_style": "casual",
        "variable_naming": "meme",
        "indent_variation": True,
        "add_dead_code": True,
        "preferred_phrases": ["bruh", "lol", "ngmi", "based af"]
    }
    """)
except Exception as e:
    print("\nHumanization failed with:")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")
input("Press Enter to close... (copy the humanized code if it worked!)")
