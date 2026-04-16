def get_credit_approval(metrics):
    """
    Logica di approvazione basata sulle metriche calcolate
    """
    dscr = metrics.get('dscr', 0)
    leverage = metrics.get('leverage', 0)
    margin = metrics.get('margin', 0)
    ebitda = metrics.get('ebitda', 0)
    short_debt = metrics.get('short_debt', 0)

    score = 0
    if dscr >= 1.2: score += 40
    if leverage <= 3: score += 30
    if margin > 10: score += 20
    if ebitda > 0: score += 10

    if score >= 70:
        decision, rating, color = "APPROVATO", "A", "#00CC66"
    elif score >= 40:
        decision, rating, color = "REVISIONE", "B", "#FFCC00"
    else:
        decision, rating, color = "NEGATO", "C", "#FF3300"

    return {
        "score": score,
        "decision": decision,
        "rating": rating,
        "color": color,
        "estimated_credit": int(max(0, (ebitda * 3) - short_debt))
    }
