# Add near top
from humanizer import detect_language, calculate_soul_score, humanize_code

# In your scan/command handler (example structure)
def handle_scan(args):
    file_path = args.file
    if not os.path.exists(file_path):
        print("File not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    lang = detect_language(file_path)
    if lang == 'unknown':
        print(f"Unsupported file type: {file_path}")
        return

    score = calculate_soul_score(code, lang)
    print(f"Soul Score for {file_path}: {score}/100 ({'Likely AI' if score < 40 else 'Human-like'})")

    if score < 50 and args.auto_humanize:  # Add --auto-humanize flag
        print("Auto-humanizing...")
        humanized = humanize_code(code, lang, intensity=0.8)
        output_path = file_path.replace('.', '_humanized.')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(humanized)
        print(f"Humanized version saved to: {output_path}")
        new_score = calculate_soul_score(humanized, lang)
        print(f"New Soul Score: {new_score}/100")
