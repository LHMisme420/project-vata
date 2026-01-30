def explain_score(score, reasons):
    return "\n".join([
        f"Soul Score: {score}",
        "Reasoning:",
        *[f"- {r}" for r in reasons]
    ])
