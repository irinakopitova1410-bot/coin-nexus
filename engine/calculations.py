from dataclasses import dataclass, field
from typing import Dict, List

# ══════════════════════════════════════════════════
# ALTMAN Z-SCORE
# ══════════════════════════════════════════════════

@dataclass
class AltmanResult:
    z_score: float
    model: str
    variables: Dict[str, float]
    zone: str
    zone_label: str
    bankruptcy_probability: float
    rating: str
    recommendation: str
    projections: List[Dict]
    thresholds: Dict[str, float]

def _zone_color(zone: str) -> str:
    return {"safe": "🟢 ZONA SICURA", "grey": "🟡 ZONA GRIGIA", "distress": "🔴 ZONA DI PERICOLO"}[zone]

def _prob_from_z(z: float, safe_min: float, grey_min: float) -> float:
    if z >= safe_min:
        return max(1.0, 5.0 - (z - safe_min) * 2)
    elif z >= grey_min:
        ratio = (z - grey_min) / (safe_min - grey_min)
        return 55 - ratio * 35
    else:
        return min(97.0, 55 + (grey_min - z) / grey_min * 42)

def _projections(z: float) -> List[Dict]:
    return [
        {"Anno": f"+{y}", "Scenario Base": round(z * (1 + g), 3), "Scenario Stress": round(z * (1 - s), 3)}
        for y, g, s in [(1, 0.12, 0.08), (2, 0.26, 0.15), (3, 0.42, 0.22), (4, 0.60, 0.28)]
    ]

def altman_z_original(working_capital, total_assets, retained_earnings, ebit,
                       market_cap, total_liabilities, revenue) -> AltmanResult:
    """Z-Score 1968 — Quotate manifatturiere"""
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = revenue / total_assets
    z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5

    zone = "safe" if z > 2.99 else ("grey" if z >= 1.81 else "distress")
    rating = "AAA/AA" if z > 2.99 else ("BB/B" if z >= 1.81 else "CCC/D")
    prob = _prob_from_z(z, 2.99, 1.81)

    return AltmanResult(
        z_score=round(z, 3), model="Altman Z-Score (1968) — Aziende Quotate",
        variables={"X1 (Capital/Assets)": round(x1,4), "X2 (RE/Assets)": round(x2,4),
                   "X3 (EBIT/Assets)": round(x3,4), "X4 (Mkt Cap/Liab)": round(x4,4),
                   "X5 (Revenue/Assets)": round(x5,4)},
        zone=zone, zone_label=_zone_color(zone),
        bankruptcy_probability=round(prob, 2), rating=rating,
        recommendation=_rec(zone), projections=_projections(z),
        thresholds={"safe": 2.99, "grey_low": 1.81}
    )

def altman_z_prime(working_capital, total_assets, retained_earnings, ebit,
                    book_equity, total_liabilities, revenue) -> AltmanResult:
    """Z'-Score 1983 — Aziende private"""
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = book_equity / total_liabilities
    x5 = revenue / total_assets
    z = 0.717*x1 + 0.847*x2 + 3.107*x3 + 0.420*x4 + 0.998*x5

    zone = "safe" if z > 2.9 else ("grey" if z >= 1.23 else "distress")
    rating = "AAA/AA" if z > 2.9 else ("BB/B" if z >= 1.23 else "CCC/D")
    prob = _prob_from_z(z, 2.9, 1.23)

    return AltmanResult(
        z_score=round(z, 3), model="Altman Z'-Score (1983) — Aziende Private",
        variables={"X1 (Capital/Assets)": round(x1,4), "X2 (RE/Assets)": round(x2,4),
                   "X3 (EBIT/Assets)": round(x3,4), "X4 (Equity/Liab)": round(x4,4),
                   "X5 (Revenue/Assets)": round(x5,4)},
        zone=zone, zone_label=_zone_color(zone),
        bankruptcy_probability=round(prob, 2), rating=rating,
        recommendation=_rec(zone), projections=_projections(z),
        thresholds={"safe": 2.9, "grey_low": 1.23}
    )

def altman_z_doubleprime(working_capital, total_assets, retained_earnings, ebit,
                          book_equity, total_liabilities) -> AltmanResult:
    """Z''-Score 1995 — Non manifatturiere/Servizi"""
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = book_equity / total_liabilities
    z = 6.56*x1 + 3.26*x2 + 6.72*x3 + 1.05*x4

    zone = "safe" if z > 2.6 else ("grey" if z >= 1.1 else "distress")
    rating = "AAA/AA" if z > 2.6 else ("BB/B" if z >= 1.1 else "CCC/D")
    prob = _prob_from_z(z, 2.6, 1.1)

    return AltmanResult(
        z_score=round(z, 3), model="Altman Z''-Score (1995) — Non Manifatturiere",
        variables={"X1 (Capital/Assets)": round(x1,4), "X2 (RE/Assets)": round(x2,4),
                   "X3 (EBIT/Assets)": round(x3,4), "X4 (Equity/Liab)": round(x4,4)},
        zone=zone, zone_label=_zone_color(zone),
        bankruptcy_probability=round(prob, 2), rating=rating,
        recommendation=_rec(zone), projections=_projections(z),
        thresholds={"safe": 2.6, "grey_low": 1.1}
    )

def _rec(zone: str) -> str:
    return {
        "safe": "✅ Struttura finanziaria solida. L'azienda non presenta segnali di crisi. Monitoraggio ordinario annuale.",
        "grey": "⚠️ Attenzione: l'azienda si trova nella zona grigia. Raccomandato monitoraggio trimestrale e revisione del piano finanziario.",
        "distress": "🚨 URGENTE: l'azienda è in zona di pericolo. Intervento immediato: ristrutturazione del debito, aumento del capitale, riduzione dei costi."
    }[zone]


# ══════════════════════════════════════════════════
# CREDIT SCORING
# ══════════════════════════════════════════════════

@dataclass
class CreditResult:
    score: float
    rating: str
    decision: str
    dscr: float
    leverage: float
    ebitda_margin: float
    current_ratio: float
    components: Dict[str, float]
    max_credit: float
    recommendations: List[str]
    decision_color: str

def _score_dscr(v):
    if v >= 2.0: return 100
    elif v >= 1.5: return 80 + (v-1.5)/0.5*20
    elif v >= 1.25: return 60 + (v-1.25)/0.25*20
    elif v >= 1.0: return 40 + (v-1.0)/0.25*20
    elif v >= 0.75: return 20 + (v-0.75)/0.25*20
    return max(0, v/0.75*20)

def _score_leverage(v):
    if v <= 0.5: return 100
    elif v <= 1.0: return 80 + (1.0-v)/0.5*20
    elif v <= 2.0: return 60 + (2.0-v)/1.0*20
    elif v <= 3.0: return 40 + (3.0-v)/1.0*20
    elif v <= 5.0: return 20 + (5.0-v)/2.0*20
    return max(0, 20-(v-5)*4)

def _score_ebitda(v):
    if v >= 20: return 100
    elif v >= 15: return 80 + (v-15)/5*20
    elif v >= 10: return 60 + (v-10)/5*20
    elif v >= 5: return 40 + (v-5)/5*20
    elif v >= 0: return v/5*40
    return 0

def _score_cr(v):
    if v >= 2.0: return 100
    elif v >= 1.5: return 75 + (v-1.5)/0.5*25
    elif v >= 1.0: return 40 + (v-1.0)/0.5*35
    elif v >= 0.75: return 15 + (v-0.75)/0.25*25
    return max(0, v/0.75*15)

def calculate_credit_score(ebit, depreciation, interest_expense, debt_repayment,
                            total_debt, ebitda, net_revenue, current_assets,
                            current_liabilities, total_equity) -> CreditResult:
    dscr = (ebit+depreciation)/(interest_expense+debt_repayment) if (interest_expense+debt_repayment) > 0 else 5.0
    leverage = total_debt/total_equity if total_equity > 0 else 10.0
    ebitda_margin = (ebitda/net_revenue*100) if net_revenue > 0 else 0
    current_ratio = current_assets/current_liabilities if current_liabilities > 0 else 3.0

    ds = _score_dscr(dscr)
    ls = _score_leverage(leverage)
    es = _score_ebitda(ebitda_margin)
    cs = _score_cr(current_ratio)
    score = max(0, min(100, ds*0.30 + ls*0.25 + es*0.25 + cs*0.20))

    rating_map = [(90,"AAA"),(80,"AA"),(70,"A"),(60,"BBB"),(50,"BB"),(40,"B"),(30,"CCC"),(20,"CC"),(0,"D")]
    rating = next(r for t,r in rating_map if score >= t)

    if score >= 65: decision, dec_color = "✅ APPROVATO", "#4ADE80"
    elif score >= 45: decision, dec_color = "🔍 IN REVISIONE", "#FCD34D"
    else: decision, dec_color = "❌ NEGATO", "#F87171"

    max_credit = max(0, ebitda*3*max(0.2,1-leverage*0.15)*(score/100)) if ebitda > 0 else 0

    recs = []
    if dscr < 1.25: recs.append("⚠️ DSCR critico: ridurre il debito o incrementare il reddito operativo")
    if leverage > 3: recs.append("⚠️ Leva finanziaria elevata: rafforzare il patrimonio netto")
    if ebitda_margin < 10: recs.append("⚠️ Margine EBITDA basso: ottimizzare i costi operativi")
    if current_ratio < 1.2: recs.append("⚠️ Liquidità corrente insufficiente: gestire il capitale circolante")
    if not recs: recs.append("✅ Profilo finanziario eccellente. Mantenere la struttura attuale.")

    return CreditResult(
        score=round(score,1), rating=rating, decision=decision,
        dscr=round(dscr,3), leverage=round(leverage,3),
        ebitda_margin=round(ebitda_margin,2), current_ratio=round(current_ratio,3),
        components={"DSCR (30%)": round(ds,1), "Leverage (25%)": round(ls,1),
                    "EBITDA Margin (25%)": round(es,1), "Current Ratio (20%)": round(cs,1)},
        max_credit=round(max_credit,0), recommendations=recs, decision_color=dec_color
    )


# ══════════════════════════════════════════════════
# AUDIT ISA 320
# ══════════════════════════════════════════════════

@dataclass
class AuditResult:
    materiality: float
    performance_materiality: float
    trivial_threshold: float
    score: int
    judgment: str
    judgment_color: str
    risks: List[str]
    recommendations: List[str]

def calculate_audit(gross_profit, total_assets, net_revenue, pre_tax_income,
                    internal_control_score, error_rate, risk_level) -> AuditResult:
    opts = {}
    if abs(gross_profit) > 0: opts["profit"] = abs(gross_profit)*0.05
    if total_assets > 0: opts["assets"] = total_assets*0.01
    if net_revenue > 0: opts["revenue"] = net_revenue*0.005
    materiality = min(opts.values()) if opts else 10000

    pm_factor = {"low": 0.80, "medium": 0.75, "high": 0.65}.get(risk_level, 0.75)
    perf_mat = materiality * pm_factor
    trivial = materiality * 0.03

    ic_pts = (internal_control_score/10)*40
    err_pen = min(40, error_rate*4)
    score = int(max(0, min(100, 60 + ic_pts - err_pen)))

    if score >= 85:
        judgment = "✅ GIUDIZIO SENZA RILIEVI"
        jcolor = "#4ADE80"
    elif score >= 70:
        judgment = "🔍 GIUDIZIO CON RILIEVI"
        jcolor = "#FCD34D"
    elif score >= 55:
        judgment = "⚠️ GIUDIZIO AVVERSO PARZIALE"
        jcolor = "#F97316"
    else:
        judgment = "❌ IMPOSSIBILITÀ DI ESPRIMERE GIUDIZIO"
        jcolor = "#F87171"

    risks = []
    if error_rate > 5: risks.append("🔴 Alto tasso di errori contabili rilevato")
    if internal_control_score < 5: risks.append("🔴 Sistema di controllo interno debole")
    if risk_level == "high": risks.append("🟡 Rischio inerente elevato")
    if pre_tax_income < 0: risks.append("🔴 Azienda in perdita: rischio continuità aziendale")
    if not risks: risks.append("🟢 Nessun rischio significativo identificato")

    recs = []
    if internal_control_score < 7: recs.append("Rafforzare i controlli interni e la segregazione dei compiti")
    if error_rate > 2: recs.append("Implementare riconciliazioni mensili e quadrature sistematiche")
    if risk_level == "high": recs.append("Aumentare le procedure di audit nei cicli ad alto rischio")
    if not recs: recs.append("Mantenere l'attuale struttura di controllo interno")

    return AuditResult(
        materiality=round(materiality,2), performance_materiality=round(perf_mat,2),
        trivial_threshold=round(trivial,2), score=score, judgment=judgment,
        judgment_color=jcolor, risks=risks, recommendations=recs
    )
