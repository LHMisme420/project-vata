# test_humanizer_standalone.py
# Paste this into a new file in the same folder as your humanizer.py / VataHumanizer code

try:
    from humanizer import VataHumanizer
except ImportError as e:
    print("Import failed — make sure you're running this from the folder where humanizer.py lives.")
    print("Error details:", e)
    exit(1)

# Mock soul scorer (you can remove/comment this out if your real scorer is already working)
def mock_soul_score(code: str) -> int:
    comment_count = code.count("#")
    length_bonus = len(code) // 20
    return min(95, 40 + comment_count * 8 + length_bonus)

# Temporarily replace the soul score method for this test (comment out if using real scorer)
VataHumanizer._get_soul_score = staticmethod(mock_soul_score)

# Example AI-generated code to humanize
ai_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(6)) # should print 720
"""

print("Original code:")
print(ai_code.strip())
print("-" * 50)

# Create the humanizer instance
humanizer = VataHumanizer(chaos_level="rage", target_soul_score=75)

# Optional: personalize from a GitHub username if your class supports it
# humanizer.personalize_from_github("some-username")

try:
    print("Humanizing... (this may take a few seconds depending on your implementation)")
    humanized = humanizer.humanize(ai_code)
    
    print("\nHumanized code:")
    print(humanized.strip())
    print("-" * 50)
    
    final_score = humanizer._get_soul_score(humanized)
    print(f"Final mock soul score: {final_score}")
    
    if final_score >= 75:
        print("→ Target reached! Looks good.")
    else:
        print("→ Score below target — might need more chaos / better transformations.")
        
except Exception as e:
    print("\nHumanization failed with:")
    import traceback
    traceback.print_exc()
