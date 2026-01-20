# git_provenance.py
import git
import argparse
import json
from datetime import datetime
import re

def soul_score(code):
    if not code or not code.strip():
        return 0
    score = 0
    lower = code.lower()
    if re.search(r'(todo|fixme|hack|note|optimize)', lower, re.IGNORECASE):
        score += 25
    score += min(20, len(re.findall(r'#|//|/\*|\*', code)) * 2)
    if re.search(r'(write-host|console\.log|print|debug)', lower):
        score += 15
    pipe_count = code.count('|')
    if pipe_count > 1:
        score += min(20, pipe_count * 5)
    aliases = len(re.findall(r'\b(gci|cp|%|\\?|select|sort|where|foreach)\b', lower, re.IGNORECASE))
    if aliases > 2:
        score += 15
    vars_list = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{8,}', code)
    if vars_list:
        avg = sum(len(v) for v in vars_list) / len(vars_list)
        if avg > 10: score += 15
        elif avg > 6: score += 8
    if re.search(r'sorry|hi mom|lol|coffee|idk|pray', lower):
        score += 10
    blank_ratio = code.count('\n\n') / max(1, len(code.splitlines()))
    if blank_ratio > 0.08:
        score += 10
    comment_count = len(re.findall(r'#|//|/\*|\*', code))
    if score < 30 and len(code) > 200 and comment_count == 0:
        score -= 25
    return max(0, min(100, score))

def scan_repo(repo_path='.', branch='main', verbose=False):
    try:
        repo = git.Repo(repo_path)
        results = []
        total_score = 0
        file_count = 0

        for commit in repo.iter_commits(branch):
            date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
            for file_path in commit.stats.files.keys():
                if file_path.endswith(('.py', '.ps1', '.js', '.ts')):
                    try:
                        blob = commit.tree / file_path
                        code = blob.data_stream.read().decode('utf-8', errors='ignore')
                        score = soul_score(code)
                        results.append({
                            "commit": commit.hexsha[:8],
                            "date": date,
                            "file": file_path,
                            "score": score
                        })
                        total_score += score
                        file_count += 1
                        if verbose:
                            print(f"{date} {commit.hexsha[:8]} {file_path} {score}/100")
                    except:
                        pass

        if file_count == 0:
            return {"error": "No code files found"}

        avg = round(total_score / file_count, 1)
        return {
            "repo": repo_path,
            "branch": branch,
            "humanity_index": avg,
            "files_scanned": file_count,
            "results": results[-20:]  # last 20 for brevity
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VATA Git Soul Scanner")
    parser.add_argument("--path", default=".", help="Repo path (default: current dir)")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    result = scan_repo(args.path, args.branch, args.verbose)
    print(json.dumps(result, indent=2))
    if "humanity_index" in result:
        print(f"\nHumanity Index: {result['humanity_index']}/100")