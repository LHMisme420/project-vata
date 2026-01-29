# vata.py — Complete standalone version with serious check and legacy humanize mode
# Run with: python vata.py check yourfile.py --verbose
# or: python vata.py humanize yourfile.py
# No dependencies needed — built-in Python only

import argparse
import sys
import ast
from pathlib import Path

def simple_complexity_estimate(code: str) -> int:
    """Basic cyclomatic complexity using ast — no deps."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return -1

    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
    return complexity

def check_file(filename: str, verbose: bool = False):
    """Serious code quality check."""
    path = Path(filename)
    if not path.is_file():
        print(f"Error: File not found → {filename}")
        sys.exit(1)

    try:
        with path.open(encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    lines = code.splitlines()
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comments = sum(1 for line in lines if line.strip().startswith('#'))
    complexity = simple_complexity_estimate(code)

    print(f"\nFile checked: {filename}")
    print("─" * 50)
    print(f"Total lines:      {total}")
    print(f"Blank lines:      {blank} ({blank / total * 100:.1f}% if total > 0 else 0)")
    print(f"Comment lines:    {comments} ({comments / total * 100:.1f}% if total > 0 else 0)")
    print(f"Complexity est.:  {complexity if complexity >= 0 else 'Syntax error'}")

    if total > 0:
        comment_pct = (comments / total) * 100
        quality = "Good" if comment_pct > 10 and complexity < 20 else "Needs improvement"
        print(f"Quality vibe:     {quality}")
    else:
        print("File is empty")

    if verbose:
        print("\nVerbose details:")
        print(f"  File size: {len(code)} bytes")
        print("  First 5 lines:")
        for i, line in enumerate(lines[:5], 1):
            print(f"    L{i:2}: {line.rstrip()}")

def humanize_file(filename: str):
    """Legacy fun mode — meme humanizer demo."""
    path = Path(filename)
    if not path.is_file():
        print(f"Error: File not found → {filename}")
        sys.exit(1)

    try:
        with path.open(encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"\nHumanizing: {filename}")
    print("─" * 50)
    print("HUMANIZED VERSION (demo):")
    print("# RAGE ONE-LINER frfr 😂 # sigma 💀")
    print("basedCounter = ngmiVar.frfrVal  # based af")
    print(f"ORIGINAL LINES: {len(code.splitlines())}")
    print("SOUL SCORE: 98/100  (target reached 🔥)")
    print("\nDIFF (demo):")
    print("--- original")
    print("+++ humanized")
    print("@@ -1 +1 @@")
    print("+ # added human vibe 💀")

def main():
    parser = argparse.ArgumentParser(description="VATA — Code Quality Checker")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Serious check command
    check_parser = subparsers.add_parser('check', help='Analyze code quality')
    check_parser.add_argument('file', help='Python file to check')
    check_parser.add_argument('--verbose', action='store_true', help='Show more details')

    # Legacy humanize command
    human_parser = subparsers.add_parser('humanize', help='Legacy fun humanization demo')
    human_parser.add_argument('file', help='File to humanize')

    args = parser.parse_args()

    if args.command == 'check':
        check_file(args.file, args.verbose)
    elif args.command == 'humanize':
        humanize_file(args.file)

if __name__ == '__main__':
    main()
