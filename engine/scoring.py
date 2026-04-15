def compute_metrics(d):

    dscr = d["ebitda"] / d["debt"] if d["debt"] else 0
    liquidity = (d["cash"] + d["receivables"]) / (d["payables"] + 1)

    score = 0
    reasons = []

    if dscr > 1.5:
        score += 40
        reasons.append("DSCR solido")

    if liquidity > 1.2:
        score += 30
        reasons.append("Liquidità buona")

    if d["debt"] < d["ebitda"] * 3:
        score += 30
        reasons.append("Leva sostenibile")

    return {
        "score": score,
        "reasons": reasons
    }
