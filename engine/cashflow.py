"""
NEXUS Finance Pro — Cash Flow Analysis Engine
Metodo indiretto, proiezioni, analisi covenant, stress test.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


@dataclass
class CashFlowStatement:
    # Operativo
    net_income: float
    depreciation: float
    delta_working_capital: float
    other_operating: float
    operating_cashflow: float

    # Investimenti
    capex: float
    acquisitions: float
    investing_cashflow: float

    # Finanziario
    debt_issued: float
    debt_repaid: float
    dividends: float
    financing_cashflow: float

    # Totali
    free_cashflow: float
    net_change: float

    # KPI
    cash_conversion_ratio: float   # OCF / Net Income
    capex_intensity: float         # CapEx / Revenue
    fcf_margin: float              # FCF / Revenue
    reinvestment_rate: float       # CapEx / (CapEx + FCF)

    # Proiezioni
    projections: List[Dict]
    covenants: List[Dict]
    alerts: List[str]


def calculate_cashflow(data: Dict[str, float]) -> CashFlowStatement:
    """
    Calcola il rendiconto finanziario con metodo indiretto.
    """
    net_income = data.get("net_income", 0)
    depreciation = data.get("depreciation", 0)
    ebit = data.get("ebit", 0)
    ebitda = data.get("ebitda", ebit + depreciation)
    revenue = data.get("revenue", 1)
    total_debt = data.get("total_debt", 0)
    interest_expense = data.get("interest_expense", 0)
    tax_expense = data.get("tax_expense", net_income * 0.28)

    # Working capital
    current_assets = data.get("current_assets", 0)
    current_liabilities = data.get("current_liabilities", 0)
    prev_current_assets = data.get("prev_current_assets", current_assets * 0.95)
    prev_current_liabilities = data.get("prev_current_liabilities", current_liabilities * 0.95)
    delta_ca = current_assets - prev_current_assets
    delta_cl = current_liabilities - prev_current_liabilities
    delta_wc = -(delta_ca - delta_cl)  # Aumento WC = assorbimento cassa

    # CapEx
    fixed_assets = data.get("fixed_assets", 0)
    prev_fixed_assets = data.get("prev_fixed_assets", fixed_assets * 0.9)
    capex = max(0, fixed_assets - prev_fixed_assets + depreciation)
    if "capex" in data:
        capex = data["capex"]

    # Acquisizioni
    acquisitions = data.get("acquisitions", 0)

    # Finanziamento
    debt_issued = data.get("debt_issued", 0)
    debt_repaid = data.get("debt_repaid", total_debt * 0.1)
    dividends = data.get("dividends", max(0, net_income * 0.3) if net_income > 0 else 0)

    # Calcoli
    operating_cf = net_income + depreciation + delta_wc + data.get("other_operating", 0)
    investing_cf = -(capex + acquisitions)
    financing_cf = debt_issued - debt_repaid - dividends

    free_cf = operating_cf - capex
    net_change = operating_cf + investing_cf + financing_cf

    # KPI
    ccr = (operating_cf / net_income) if net_income != 0 else 0
    capex_intensity = capex / revenue if revenue > 0 else 0
    fcf_margin = free_cf / revenue if revenue > 0 else 0
    reinv_rate = capex / (capex + free_cf) if (capex + free_cf) > 0 else 0

    # Proiezioni (5 anni, scenario base + stress)
    projections = []
    base_growth = 0.05
    stress_growth = -0.03
    for y in range(1, 6):
        base_ocf = operating_cf * ((1 + base_growth) ** y)
        stress_ocf = operating_cf * ((1 + stress_growth) ** y)
        base_capex = capex * ((1 + 0.03) ** y)
        projections.append({
            "Anno": f"+{y}",
            "OCF Base": round(base_ocf, 0),
            "FCF Base": round(base_ocf - base_capex, 0),
            "OCF Stress": round(stress_ocf, 0),
            "FCF Stress": round(stress_ocf - base_capex, 0),
        })

    # Covenant check
    covenants = []
    if total_debt > 0 and ebitda > 0:
        net_debt_ebitda = total_debt / ebitda
        covenants.append({
            "Covenant": "Net Debt / EBITDA",
            "Valore": round(net_debt_ebitda, 2),
            "Limite tipico": "≤ 3.5x",
            "Status": "✅ OK" if net_debt_ebitda <= 3.5 else "🔴 VIOLATO",
        })
    if interest_expense > 0 and ebit > 0:
        icr = ebit / interest_expense
        covenants.append({
            "Covenant": "Interest Coverage (EBIT/Interessi)",
            "Valore": round(icr, 2),
            "Limite tipico": "≥ 2.5x",
            "Status": "✅ OK" if icr >= 2.5 else "🔴 VIOLATO",
        })
    if total_debt > 0 and (total_debt + data.get("equity", 1)) > 0:
        lev = total_debt / (total_debt + data.get("equity", 1))
        covenants.append({
            "Covenant": "Leverage Ratio (Debt/Capital)",
            "Valore": round(lev, 2),
            "Limite tipico": "≤ 0.65",
            "Status": "✅ OK" if lev <= 0.65 else "🔴 VIOLATO",
        })

    # Alert
    alerts = []
    if free_cf < 0:
        alerts.append("🔴 Free Cash Flow negativo: l'azienda brucia cassa")
    if ccr < 0.5 and net_income > 0:
        alerts.append("⚠️ Cash conversion bassa: utili non si trasformano in cassa")
    if capex_intensity > 0.15:
        alerts.append(f"⚠️ CapEx intensity elevata ({capex_intensity:.1%}): investimenti pesanti")
    if delta_wc < -revenue * 0.05:
        alerts.append("⚠️ Capitale circolante assorbe cassa: monitorare ciclo commerciale")
    if free_cf > 0 and reinv_rate < 0.3:
        alerts.append("ℹ️ Basso reinvestimento: alta distribuzione o accumulo cassa")

    return CashFlowStatement(
        net_income=net_income,
        depreciation=depreciation,
        delta_working_capital=delta_wc,
        other_operating=data.get("other_operating", 0),
        operating_cashflow=round(operating_cf, 0),
        capex=round(capex, 0),
        acquisitions=acquisitions,
        investing_cashflow=round(investing_cf, 0),
        debt_issued=debt_issued,
        debt_repaid=round(debt_repaid, 0),
        dividends=round(dividends, 0),
        financing_cashflow=round(financing_cf, 0),
        free_cashflow=round(free_cf, 0),
        net_change=round(net_change, 0),
        cash_conversion_ratio=round(ccr, 3),
        capex_intensity=round(capex_intensity, 4),
        fcf_margin=round(fcf_margin, 4),
        reinvestment_rate=round(reinv_rate, 4),
        projections=projections,
        covenants=covenants,
        alerts=alerts,
    )
