from vata_cli import run_analysis
from vata_json import to_json
from vata_fingerprint import fingerprint

def analyze(code, persona="default", as_json=False):
    score, reasons, fairness, humanized, votes, zk = run_analysis(code, persona, return_data=True)
    fp = fingerprint(code)

    if as_json:
        return to_json(score, reasons, fairness, humanized, votes, zk)

    return {
        "score": score,
        "reasons": reasons,
        "fairness": fairness,
        "humanized": humanized,
        "votes": votes,
        "zk": zk,
        "fingerprint": fp
    }
