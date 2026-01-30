# vata.py
import argparse
import json
import sys
from pathlib import Path
from src.vata.core import score_soul
from src.vata.humanizer import inject_soul

def main():
    parser = argparse.ArgumentParser(description="Project VATA – Soul Checker & Humanizer")
    parser.add_argument("file", type=str, help="Path to code file")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model")
    parser.add_argument("--behavioral", action="store_true", help="Enable behavioral checks")
    parser.add_argument("--auto-humanize", action="store_true", help="Inject soul if low")
    parser.add_argument("--output", default="json", choices=["json", "text"], help="Output format")
    parser.add_argument("--humanized-file", type=str, help="Save humanized code here")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    code = file_path.read_text(encoding="utf-8")

    result = score_soul(code)

    if args.auto_humanize and result["soul_score"] < 71:
        humanized = inject_soul(code)
        result["humanized_code"] = humanized
        if args.humanized_file:
            Path(args.humanized_file).write_text(humanized)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Soul Score: {result['soul_score']}/100 ({result['category']})")
        print("Metrics:", result["metrics"])
        if "risks" in result:
            print("Risks:", result["risks"])
        if "humanized_code" in result:
            print("\nHumanized:\n", result["humanized_code"])

if __name__ == "__main__":
    main()
