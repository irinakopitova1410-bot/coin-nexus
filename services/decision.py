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
