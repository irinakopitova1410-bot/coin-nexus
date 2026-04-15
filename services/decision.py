def credit_decision(m):

    score = 0
    reasons = []

    if m["dscr"] > 1.5:
        score += 40
        reasons.append("DSCR solido")

    if m["liquidity"] > 1.2:
        score += 30
        reasons.append("Liquidità buona")

    if m["leverage"] < 3:
        score += 30
        reasons.append("Leva controllata")

    if score >= 80:
        return {"status": "APPROVED", "score": score, "reason": reasons}

    elif score >= 50:
        return {"status": "CONDITIONAL", "score": score, "reason": reasons}

    return {"status": "REJECTED", "score": score, "reason": reasons}
