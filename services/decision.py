def calculate_metrics(data):
    """
    Estrae metriche finanziarie per credit decision engine
    """
    # Conversione sicura in float
    rev = float(data.get('revenue', 0))
    ebitda = float(data.get('ebitda', 0))
    debt = float(data.get('debt', 0))
    short_debt = float(data.get('short_debt', 0))

    # --- DSCR (Debt Service Coverage Ratio) ---
    # Simulazione servizio del debito: 20% quota capitale + 5% interessi stimati
    annual_service = (debt * 0.20) + (debt * 0.05)
    dscr = ebitda / annual_service if annual_service > 0 else (10.0 if ebitda > 0 else 0.0)

    # --- LEVERAGE (PFN/EBITDA) ---
    leverage = debt / ebitda if ebitda > 0 else (99.0 if debt > 0 else 0.0)

    # --- EBITDA MARGIN ---
    margin = (ebitda / rev * 100) if rev > 0 else 0.0

    # --- LIQUIDITY PRESSURE ---
    liquidity_pressure = short_debt / ebitda if ebitda > 0 else 99.0

    return {
        "dscr": round(dscr, 2),
        "leverage": round(leverage, 2),
        "margin": round(margin, 2),
        "liquidity_pressure": round(liquidity_pressure, 2),
        "ebitda": ebitda,
        "revenue": rev,
        "debt": debt,
        "short_debt": short_debt
    }
