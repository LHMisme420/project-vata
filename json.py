import json

def to_json(score, reasons, fairness, humanized, votes, zk):
    return json.dumps({
        "soul_score": score,
        "breakdown": reasons,
        "fairness_ethics": fairness.split("\n"),
        "humanized": humanized.split("\n"),
        "swarm_votes": votes.split("\n"),
        "zk_proof": zk.split("\n")
    }, indent=2)
