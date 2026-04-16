def calculate_metrics(data):
    revenue = data.get('revenue', 0)
    ebitda = data.get('ebitda', 0)
    debt = data.get('debt', 0)
    short_debt = data.get('short_debt', 0)
    cash = data.get('cash', 0)
    receivables = data.get('receivables', 0)

    # --- PROTEZIONI ---
    ebitda_safe = ebitda if ebitda > 0 else 1

    # --- DSCR (più credibile) ---
    interest_rate = 0.05
    duration_years = 5

    annual_principal = debt / duration_years if debt > 0 else 0
    annual_interest = debt * interest_rate
    annual_service = annual_principal + annual_interest

    dscr = ebitda / annual_service if annual_service > 0 else 0

    # --- LEVERAGE ---
    leverage = debt / ebitda_safe

    # --- MARGINE EBITDA ---
    margin = (ebitda / revenue) if revenue > 0 else 0

    # --- LIQUIDITÀ (CRUCIALE 💰) ---
    current_assets = cash + receivables
    current_ratio = current_assets / short_debt if short_debt > 0 else 99

    # --- QUALITÀ FLUSSI ---
    cash_buffer = cash / short_debt if short_debt > 0 else 1

    return {
        "dscr": round(dscr, 2),
        "leverage": round(leverage, 2),
        "margin": round(margin, 2),
        "current_ratio": round(current_ratio, 2),
        "cash_buffer": round(cash_buffer, 2),

        # extra utili per decision.py
        "ebitda": ebitda,
        "revenue": revenue,
        "debt": debt,
        "short_debt": short_debt
    }
