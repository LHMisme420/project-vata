from pathlib import Path
from vata_cli import run_analysis

def analyze_folder(folder, persona="default"):
    folder = Path(folder)
    results = {}

    for file in folder.rglob("*.*"):
        if file.suffix in [".py", ".js", ".ts", ".java", ".cpp"]:
            code = file.read_text(errors="ignore")
            score, reasons, fairness, humanized, votes, zk = run_analysis(code, persona, return_data=True)
            results[str(file)] = {
                "score": score,
                "reasons": reasons,
                "fairness": fairness,
                "votes": votes,
            }

    return results
