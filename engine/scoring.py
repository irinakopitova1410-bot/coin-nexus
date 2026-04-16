def calculate_metrics(data):
    """
    Calcolo metriche + preparazione decision engine
    """

    rev = float(data.get('revenue', 0))
    ebitda = float(data.get('ebitda', 0))
    debt = float(data.get('debt', 0))

    # --- DSCR ---
    debt_service = (debt * 0.20) + (debt * 0.05)

    dscr = ebitda / debt_service if debt_service > 0 else (10.0 if ebitda > 0 else 0.0)

    # --- LEVERAGE ---
    leverage = debt / ebitda if ebitda > 0 else (99.0 if debt > 0 else 0.0)

    # --- MARGIN ---
    margin = (ebitda / rev * 100) if rev > 0 else 0.0

    # --- SCORE BASE (💰 QUESTO È LA CHIAVE) ---
    score = 0

    # DSCR score
    if dscr >= 1.5:
        score += 40
    elif dscr >= 1.1:
        score += 25
    else:
        score += 10

    # Leverage score
    if leverage <= 3:
        score += 40
    elif leverage <= 5:
        score += 25
    else:
        score += 10

    # Margin score
    if margin >= 15:
        score += 20
    elif margin >= 5:
        score += 10
    else:
        score += 5

    # --- CREDIT ESTIMATION ---
    estimated_credit = max(0, ebitda * 4 - debt)

    # --- RISK LEVEL ---
    if score >= 75:
        rating = "A"
        decision = "APPROVATO"
        risk = "LOW"
    elif score >= 55:
        rating = "BBB"
        decision = "REVISIONE"
        risk = "MEDIUM"
    else:
        rating = "CCC"
        decision = "NEGATO"
        risk = "HIGH"
return {
    "dscr": dscr,
    "leverage": leverage,
    "margin": margin,
    "liquidity_pressure": liquidity_pressure, # <--- Verifica questo nome!
    # ... altri dati
}
        # 🔥 BUSINESS OUTPUT
        "score": score,
        "rating": rating,
        "decision": decision,
        "risk": risk,
        "estimated_credit": round(estimated_credit, 2),

        # 🔥 EXTRA (per vendita)
        "message": f"{decision} - Risk {risk}"
    }
