def compute_score(f):

    score = 0
    explanation = []

    quick_ratio = (f["cash"] + f["receivables"]) / f["payables"] if f["payables"] else 0
    nwc = f["current_assets"] - f["payables"]

    # LIQUIDITÀ
    if quick_ratio > 1.5:
        score += 40
        explanation.append("Liquidità molto forte")
    elif quick_ratio > 1:
        score += 25
        explanation.append("Liquidità sufficiente")
    else:
        score += 10
        explanation.append("Liquidità critica")

    # STRUTTURA
    if nwc > 0:
        score += 35
        explanation.append("Capitale circolante positivo")
    else:
        score += 10
        explanation.append("Capitale circolante negativo")

    # STABILITÀ
    if f["cash"] > f["payables"]:
        score += 25
        explanation.append("Copertura debiti immediata")

    return min(score, 100), explanation


def risk_label(score):

    if score >= 80:
        return "🟢 BASSO RISCHIO"
    elif score >= 60:
        return "🟡 RISCHIO MEDIO"
    elif score >= 40:
        return "🟠 RISCHIO ALTO"
    else:
        return "🔴 RISCHIO CRITICO"
