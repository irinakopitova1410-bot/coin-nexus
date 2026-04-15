def calculate_metrics(data):
    rev = data.get('revenue', 0)
    ebitda = data.get('ebitda', 0)
    debt = data.get('debt', 0)
    
    # Calcolo DSCR semplificato
    annual_service = (debt / 5) + (debt * 0.05)
    dscr = ebitda / annual_service if annual_service > 0 else 0
    
    # Leverage
    leverage = debt / ebitda if ebitda > 0 else 0
    
    return {
        "dscr": round(dscr, 2),
        "leverage": round(leverage, 2),
        "margin": round((ebitda / rev * 100), 2) if rev > 0 else 0
    }
