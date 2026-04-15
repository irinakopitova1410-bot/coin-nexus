def get_credit_approval(metrics):
    dscr = metrics.get('dscr', 0)
    leverage = metrics.get('leverage', 0)
    
    if dscr >= 1.5 and leverage <= 3.0:
        return {"rating": "AAA", "decision": "APPROVATO", "color": "#00CC66"}
    elif dscr >= 1.1:
        return {"rating": "BBB", "decision": "REVISIONE", "color": "#FFCC00"}
    else:
        return {"rating": "CCC", "decision": "NEGATO", "color": "#FF3300"}
