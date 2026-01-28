# Security Policy – Project VATA

## How to Report a Security Problem
If you find a possible bug or weakness (in the code, ZK proofs, humanizer, guardian, etc.):
- Use GitHub's "Report a Vulnerability" button here: [Security Advisories](https://github.com/LHMisme420/project-vata/security/advisories/new)
- Or email me privately: lhmisme+security@gmail.com (replace with your real email if you want)

**Please do NOT** post details publicly in issues or on X until we fix it.

We'll reply within a couple of days and keep you updated. If it's a real issue, we'll credit you (if you want) in the README or release notes.

## What We Currently Support
- Only the `main` branch is actively watched and fixed.
- Older versions aren't supported anymore.

## Quick Security Status
- **ZK Proofs & Circuits**: Built with Circom and Groth16. No outside expert review yet—we plan to get one in early 2026.
- **Code Humanizer & Guardian**: Checks for secrets and bad patterns, but not formally proven perfect.
- **Dependencies**: We watch for known issues (Dependabot is on).
- Main worries right now: Possible mistakes in the ZK math (we're checking ourselves first) and the trusted setup step in Groth16.

Thanks for helping keep VATA safe!
