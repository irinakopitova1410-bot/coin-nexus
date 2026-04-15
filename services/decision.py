# services/decision.py

def get_credit_approval(metrics):
    """
    Logica di approvazione del credito basata su soglie bancarie.
    """
    dscr = metrics.get('dscr', 0)
    leverage = metrics.get('leverage', 0)
    
    # Regole di business (Credit Policy)
    if dscr > 1.4 and leverage < 3.5:
        return {
            "decision": "APPROVED",
            "max_financing": "50% of Revenue",
            "risk_premium": "Low (1.5%)"
        }
    elif dscr > 1.1:
        return {
            "decision": "MANUAL_REVIEW",
            "max_financing": "25% of Revenue",
            "risk_premium": "Medium (3.0%)"
        }
    else:
        return {
            "decision": "REJECTED",
            "reason": "DSCR below safety threshold",
            "risk_premium": "N/A"
        }
