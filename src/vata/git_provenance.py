# src/vata/git_provenance.py
import git
import argparse
from pathlib import Path
import hashlib
import json
from datetime import datetime

# Reuse your soul_score from HF/humanizer (paste here or import)
def soul_score(code: str) -> int:
    if not code.strip():
        return 0
    score = 0
    lower = code.lower()
    import re
    comment_pat = re.compile(r'#|//|/\*|\*')
    marker_pat = re.compile(r'(todo|fixme|hack|note|optimize)', re.IGNORECASE)
    debug_pat = re.compile(r'(write-host|console\.log|print|debug|trace)', re.IGNORECASE)
    alias_pat = re.compile(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', re.IGNORECASE)

    if marker_pat.search(lower): score += 25
    score += min(20, len(comment_pat.findall(code)) * 2)
    if debug_pat.search(lower): score += 15

    pipe_count = code.count('|')
    if pipe_count > 1: score += min(20, pipe_count * 5)
    if len(alias_pat.findall(lower)) > 2: score += 15

    vars = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars:
        avg = sum(len(v) for v in vars) / len(vars)
        score += 15 if avg > 10 else 8 if avg > 6 else 0

    if re.search(r'sorry|hi mom|lol|coffee|idk|maybe|pray', lower):
        score += 10
    if code.count('\n\n') > len(code.splitlines()) * 0.08:
        score += 10

    if score < 30 and len(code) > 200 and len(comment_pat.findall(code)) == 0:
        score -= 25

    return max(0, min(100, score))

def scan_repo(repo_path: str, branch: str = "main", verbose: bool = False):
    repo = git.Repo(repo_path)
    results = []
    total_score = 0
    file_count = 0

    # Iterate over commits on branch
    for commit in repo.iter_commits(branch):
        commit_date = datetime.fromtimestamp(commit.committed_date)
        for file_path in commit.stats.files:
            if file_path.endswith(('.py', '.ps1', '.js', '.ts')):  # code files only
                try:
                    blob = commit.tree / file_path
                    code = blob.data_stream.read().decode('utf-8', errors='ignore')
                    score = soul_score(code)
                    hash_val = hashlib.sha256(code.encode()).hexdigest()[:16]

                    results.append({
                        "commit": commit.hexsha[:8],
                        "date": commit_date.isoformat(),
                        "file": file_path,
                        "soul_score": score,
                        "hash": hash_val
                    })

                    total_score += score
                    file_count += 1

                    if verbose:
                        print(f"[{commit_date}] {commit.hexsha[:8]} | {file_path} | {score}/100")
                except Exception as e:
                    if verbose:
                        print(f"Skip {file_path}: {e}")

    if file_count == 0:
        return {"error": "No code files found"}

    avg_score = total_score / file_count if file_count > 0 else 0
    humanity_index = round(avg_score, 1)  # simple average for now

    return {
        "repo": repo_path,
        "branch": branch,
        "humanity_index": humanity_index,
        "files_scanned": file_count,
        "results": results[-50:]  # last 50 for brevity
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VATA Git Provenance Scanner")
    parser.add_argument("repo_path", help="Path to local Git repo")
    parser.add_argument("--branch", default="main", help="Branch to scan")
    parser.add_argument("--verbose", action="store_true", help="Print details")
    args = parser.parse_args()

    result = scan_repo(args.repo_path, args.branch, args.verbose)
    print(json.dumps(result, indent=2))
    print(f"\nRepo Humanity Index: {result.get('humanity_index', 'N/A')}/100")