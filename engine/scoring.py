def calculate_metrics(data):
    rev = data.get('revenue', 0)
    ebitda = data.get('ebitda', 0)
    debt = data.get('debt', 0)
    
    # Calcolo DSCR (Debt Service Coverage Ratio)
    # Ipotizziamo ammortamento 5 anni + 5% interessi
    annual_service = (debt / 5) + (debt * 0.05) if debt > 0 else 0
    dscr = ebitda / annual_service if annual_service > 0 else (ebitda if ebitda > 0 else 0)
    
    # Leverage (Indebitamento)
    leverage = debt / ebitda if ebitda > 0 else (99 if debt > 0 else 0)
    
    return {
        "dscr": round(float(dscr), 2),
        "leverage": round(float(leverage), 2),
        "margin": round(float((ebitda / rev * 100) if rev > 0 else 0), 2)
    }
