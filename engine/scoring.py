def calculate_metrics(data):
    """
    Calcola i KPI (Key Performance Indicators) richiesti dalle banche.
    """
    revenue = data.get('revenue', 0)
    ebitda = data.get('ebitda', 0)
    debt = data.get('debt', 0)
    
    # 1. DSCR (Debt Service Coverage Ratio) stimato
    # Ipotizziamo un ammortamento del debito in 5 anni + 5% di interessi
    annual_debt_service = (debt / 5) + (debt * 0.05)
    dscr = ebitda / annual_debt_service if annual_debt_service > 0 else (ebitda if ebitda > 0 else 0)
    
    # 2. Leverage (Indebitamento)
    leverage = debt / ebitda if ebitda > 0 else (99 if debt > 0 else 0)
    
    # 3. Margine Operativo
    margin = (ebitda / revenue * 100) if revenue > 0 else 0
    
    return {
        "dscr": round(dscr, 2),
        "leverage": round(leverage, 2),
        "margin": round(margin, 2)
    }

def get_credit_decision(metrics):
    """
    Prende una decisione automatica basata sui parametri Basilea IV.
    """
    dscr = metrics['dscr']
    leverage = metrics['leverage']
    
    if dscr >= 2.0 and leverage <= 2.0:
        return {"score": "AAA", "decision": "APPROVATO", "color": "#00CC66"} # Verde
    elif dscr >= 1.2 and leverage <= 4.0:
        return {"score": "BBB", "decision": "REVISIONE MANUALE", "color": "#FFCC00"} # Giallo
    else:
        return {"score": "CCC", "decision": "NEGATO", "color": "#FF3300"} # Rosso
