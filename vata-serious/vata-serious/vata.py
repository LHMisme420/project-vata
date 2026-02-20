# vata.py — simple code checker with verbose support

import argparse
import sys

def check_file(filename, verbose=False):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total = len(lines)
        blank = sum(1 for line in lines if not line.strip())
        comments = sum(1 for line in lines if line.strip().startswith('#'))

        print(f"\nChecked file: {filename}")
        print("─" * 50)
        print(f"Total lines:      {total}")
        print(f"Blank lines:      {blank}")
        print(f"Comment lines:    {comments}")

        if total > 0:
            comment_pct = (comments / total) * 100
            print(f"Comment %:        {comment_pct:.1f}%")
            quality = "Good" if comment_pct > 8 else "Needs more comments / structure"
            print(f"Quality vibe:     {quality}")
        else:
            print("File is empty")

        if verbose:
            print("\nVerbose details:")
            print(f"  File size: {len(''.join(lines))} bytes")
            print("  First few lines:")
            for i, line in enumerate(lines[:6], 1):
                print(f"    Line {i:2}: {line.rstrip()}")

    except FileNotFoundError:
        print(f"File not found: {filename}")
        print("Tip: Run 'dir *.py' to list Python files here")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="VATA simple checker")
    subparsers = parser.add_subparsers(dest='cmd', required=True)

    p_check = subparsers.add_parser('check', help='Check a file')
    p_check.add_argument('file', help='File name, e.g. test.py')
    p_check.add_argument('--verbose', action='store_true', help='Show more details')

    args = parser.parse_args()

    if args.cmd == 'check':
        check_file(args.file, args.verbose)

if __name__ == '__main__':
    main()