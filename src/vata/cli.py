import argparse
import json
import sys
sys.path.append('src')

from vata.safety import get_logic_fingerprint, apply_safety_seal, verify_fingerprint

def main():
    parser = argparse.ArgumentParser(description='VATA 🛡️ — Verify human-written code')
    parser.add_argument('file', nargs='?', help='Python file to scan')
    parser.add_argument('--seal', action='store_true', help='Generate seal JSON')
    parser.add_argument('--verify', type=str, help='Verify against seal.json file')
    parser.add_argument('--code', type=str, help='Direct code string to scan')

    args = parser.parse_args()

    code = args.code or ''
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
        except:
            print("File not found")
            return

    if not code:
        print("No code provided. Use --file, --code, or pipe input.")
        return

    fp = get_logic_fingerprint(code)
    score = fp['human_score']

    print(f"VATA Scan Complete 🛡️")
    print(f"Human Soul Score: {score}/100")
    print(fp['message'])

    if args.seal:
        seal = apply_safety_seal(code, fp)
        with open('vata_seal.json', 'w') as f:
            json.dump(seal, f, indent=2)
        print("Seal saved to vata_seal.json")

    if args.verify:
        try:
            with open(args.verify, 'r') as f:
                seal_data = json.load(f)
            verified, msg = verify_fingerprint(code, seal_data)
            print(msg)
        except:
            print("Invalid seal file")

if __name__ == '__main__':
    main()
