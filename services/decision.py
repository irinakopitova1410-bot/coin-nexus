def get_credit_approval(metrics):
    dscr = metrics.get('dscr', 0)
    leverage = metrics.get('leverage', 0)
    ebitda = metrics.get('ebitda', 0)
    revenue = metrics.get('revenue', 0)
    short_debt = metrics.get('short_debt', 0)

    # --- SCORE BASE ---
    score = 0

    # DSCR
    if dscr >= 1.5:
        score += 30
        dscr_status = "ottimo"
    elif dscr >= 1.1:
        score += 20
        dscr_status = "accettabile"
    else:
        score += 5
        dscr_status = "critico"

    # Leverage
    if leverage <= 3:
        score += 30
        lev_status = "basso"
    elif leverage <= 5:
        score += 20
        lev_status = "medio"
    else:
        score += 5
        lev_status = "alto"

    # Marginalità
    margin = ebitda / revenue if revenue > 0 else 0
    if margin > 0.15:
        score += 20
        margin_status = "buona"
    elif margin > 0.05:
        score += 10
        margin_status = "media"
    else:
        score += 5
        margin_status = "bassa"

    # Debito breve
    if short_debt < ebitda:
        score += 20
        debt_status = "sotto controllo"
    else:
        score += 5
        debt_status = "critico"

    # --- DECISIONE ---
    if score >= 75:
        decision = "APPROVATO"
        rating = "A"
        color = "#00CC66"
    elif score >= 55:
        decision = "REVISIONE MANUALE"
        rating = "BBB"
        color = "#FFCC00"
    else:
        decision = "NEGATO"
        rating = "CCC"
        color = "#FF3300"

    # --- IMPORTO STIMATO (💰 IMPORTANTE) ---
    estimated_credit = max(0, ebitda * 4 - short_debt)

    # --- CRITICITÀ ---
    issues = []
    if dscr < 1.2:
        issues.append("DSCR basso")
    if leverage > 4:
        issues.append("Indebitamento elevato")
    if margin < 0.05:
        issues.append("Marginalità debole")

    # --- SUGGERIMENTI ---
    suggestions = []
    if dscr < 1.5:
        suggestions.append("Aumentare flussi di cassa operativi")
    if leverage > 3:
        suggestions.append("Ridurre il livello di debito")
    if short_debt > ebitda:
        suggestions.append("Ristrutturare debito a breve termine")

    # --- SIMULAZIONE (🔥 KILLER FEATURE) ---
    improved_score = score
    if leverage > 3:
        improved_score += 10
    if dscr < 1.5:
        improved_score += 10

    return {
        "score": score,
        "rating": rating,
        "decision": decision,
        "color": color,
        "estimated_credit": round(estimated_credit, 2),
        "issues": issues,
        "suggestions": suggestions,
        "simulation": {
            "improved_score": improved_score,
            "message": "Riducendo il debito e migliorando il cash flow, il rating può aumentare"
        }
    }
