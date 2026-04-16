def calculate_metrics(data):
    """
    Estrae metriche finanziarie per credit decision engine
    """

    rev = float(data.get('revenue', 0))
    ebitda = float(data.get('ebitda', 0))
    debt = float(data.get('debt', 0))
    short_debt = float(data.get('short_debt', 0))

    # --- DSCR ---
    annual_service = (debt * 0.20) + (debt * 0.05)

    dscr = ebitda / annual_service if annual_service > 0 else (10.0 if ebitda > 0 else 0.0)

    # --- LEVERAGE (safe) ---
    leverage = debt / ebitda if ebitda > 0 else (99.0 if debt > 0 else 0.0)

    # --- EBITDA MARGIN (utile per decision layer) ---
    margin = (ebitda / rev * 100) if rev > 0 else 0.0

    # --- LIQUIDITY SIGNAL (IMPORTANTISSIMO) ---
    liquidity_pressure = short_debt / ebitda if ebitda > 0 else 99.0

    return {
        "dscr": dscr,
        "leverage": leverage,
        "margin": margin,
        "liquidity_pressure": liquidity_pressure,

        # raw data per decision engine
        "ebitda": ebitda,
        "revenue": rev,
        "debt": debt,
        "short_debt": short_debt
    }
def get_credit_approval(metrics):
    """
    Logica di approvazione basata sulle metriche calcolate
    """
    dscr = metrics.get('dscr', 0)
    leverage = metrics.get('leverage', 0)
    margin = metrics.get('margin', 0)
    liquidity = metrics.get('liquidity_pressure', 0)
    ebitda = metrics.get('ebitda', 0)
    short_debt = metrics.get('short_debt', 0)

    score = 0
    # Logica Scoring (Esempio rapido)
    if dscr >= 1.2: score += 40
    if leverage <= 3: score += 30
    if margin > 10: score += 20
    if liquidity < 1: score += 10

    # Definizione Decisione
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
        "estimated_credit": max(0, (ebitda * 3) - short_debt),
        "issues": ["DSCR basso"] if dscr < 1.1 else [],
        "suggestions": ["Riduci debito breve"] if liquidity > 2 else [],
        "simulation": {"improved_score": score + 10}
    }
