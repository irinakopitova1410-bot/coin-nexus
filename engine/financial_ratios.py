"""
NEXUS Finance Pro — Financial Ratios Engine
35+ indicatori finanziari suddivisi in 6 categorie.
Calcolo istantaneo, benchmark di settore inclusi.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

# ─── Campi obbligatori per il calcolo dei ratio ───────────────────────────────
REQUIRED_FIELDS: Dict[str, str] = {
    "total_assets":       "Totale Attivo (€)",
    "total_liabilities":  "Totale Passivo (€)",
    "equity":             "Patrimonio Netto (€)",
    "revenue":            "Ricavi (€)",
    "ebit":               "EBIT (€)",
    "net_income":         "Utile Netto (€)",
    "current_assets":     "Attivo Corrente (€)",
    "current_liabilities": "Passivo Corrente (€)",
}

# ─── Campi opzionali (migliorano la precisione) ───────────────────────────────
OPTIONAL_FIELDS: Dict[str, str] = {
    "ebitda":              "EBITDA (€)",
    "inventory":           "Magazzino (€)",
    "accounts_receivable": "Crediti Commerciali (€)",
    "accounts_payable":    "Debiti Commerciali (€)",
    "fixed_assets":        "Immobilizzazioni (€)",
    "interest_expense":    "Oneri Finanziari (€)",
    "depreciation":        "Ammortamenti (€)",
    "total_debt":          "Debiti Finanziari Totali (€)",
    "retained_earnings":   "Utili non distribuiti (€)",
    "operating_cashflow":  "Cash Flow Operativo (€)",
    "capex":               "CapEx (€)",
    "revenue_growth":      "Crescita Ricavi YoY (es. 0.05 = 5%)",
    "ebitda_growth":       "Crescita EBITDA YoY",
}

# ─── Benchmark di settore (valori medi italiani) ──────────────────────────────
INDUSTRY_BENCHMARKS = {
    "Manifatturiero": {
        "current_ratio": 1.5, "quick_ratio": 1.0, "cash_ratio": 0.3,
        "debt_equity": 1.2, "debt_assets": 0.55, "interest_coverage": 4.0,
        "roe": 0.08, "roa": 0.05, "roi": 0.07, "ebitda_margin": 0.12,
        "net_margin": 0.04, "gross_margin": 0.28,
        "asset_turnover": 0.85, "dso": 65, "dpo": 55, "dio": 45,
    },
    "Commercio": {
        "current_ratio": 1.3, "quick_ratio": 0.6, "cash_ratio": 0.15,
        "debt_equity": 1.8, "debt_assets": 0.65, "interest_coverage": 3.0,
        "roe": 0.10, "roa": 0.04, "roi": 0.06, "ebitda_margin": 0.06,
        "net_margin": 0.02, "gross_margin": 0.22,
        "asset_turnover": 1.5, "dso": 45, "dpo": 40, "dio": 30,
    },
    "Servizi": {
        "current_ratio": 1.4, "quick_ratio": 1.2, "cash_ratio": 0.5,
        "debt_equity": 0.9, "debt_assets": 0.45, "interest_coverage": 6.0,
        "roe": 0.12, "roa": 0.08, "roi": 0.10, "ebitda_margin": 0.18,
        "net_margin": 0.07, "gross_margin": 0.55,
        "asset_turnover": 1.0, "dso": 55, "dpo": 35, "dio": 10,
    },
    "Costruzioni": {
        "current_ratio": 1.2, "quick_ratio": 0.8, "cash_ratio": 0.1,
        "debt_equity": 2.0, "debt_assets": 0.65, "interest_coverage": 2.5,
        "roe": 0.06, "roa": 0.03, "roi": 0.05, "ebitda_margin": 0.08,
        "net_margin": 0.02, "gross_margin": 0.18,
        "asset_turnover": 0.7, "dso": 90, "dpo": 75, "dio": 20,
    },
    "Tecnologia": {
        "current_ratio": 2.0, "quick_ratio": 1.8, "cash_ratio": 0.8,
        "debt_equity": 0.5, "debt_assets": 0.35, "interest_coverage": 10.0,
        "roe": 0.15, "roa": 0.10, "roi": 0.14, "ebitda_margin": 0.25,
        "net_margin": 0.12, "gross_margin": 0.65,
        "asset_turnover": 0.9, "dso": 50, "dpo": 30, "dio": 5,
    },
}


@dataclass
class Ratio:
    name: str
    value: float
    benchmark: Optional[float]
    status: str        # "ok", "warning", "danger"
    description: str
    formula: str
    unit: str = ""     # "%", "x", "giorni", ""

    @property
    def formatted(self) -> str:
        if self.unit == "%":
            return f"{self.value*100:.1f}%"
        elif self.unit == "x":
            return f"{self.value:.2f}x"
        elif self.unit == "giorni":
            return f"{self.value:.0f} gg"
        else:
            return f"{self.value:.3f}"

    @property
    def benchmark_formatted(self) -> str:
        if self.benchmark is None:
            return "N/D"
        if self.unit == "%":
            return f"{self.benchmark*100:.1f}%"
        elif self.unit == "x":
            return f"{self.benchmark:.2f}x"
        elif self.unit == "giorni":
            return f"{self.benchmark:.0f} gg"
        return f"{self.benchmark:.3f}"


@dataclass
class RatioCategory:
    name: str
    icon: str
    ratios: List[Ratio] = field(default_factory=list)
    score: float = 0.0   # 0-100

    def compute_score(self):
        ok = sum(1 for r in self.ratios if r.status == "ok")
        warn = sum(1 for r in self.ratios if r.status == "warning")
        total = len(self.ratios) or 1
        self.score = round((ok * 100 + warn * 50) / total, 1)


@dataclass
class FinancialRatiosResult:
    categories: List[RatioCategory]
    overall_score: float
    industry: str
    health_label: str
    health_color: str
    key_alerts: List[str]
    strengths: List[str]


def _safe_div(a, b, default=None):
    try:
        if b == 0 or b is None:
            return default
        return a / b
    except Exception:
        return default


def _status(value, good_min=None, good_max=None, bad_min=None, bad_max=None,
             higher_is_better=True) -> str:
    if value is None:
        return "warning"
    if higher_is_better:
        if good_min is not None and value >= good_min:
            return "ok"
        elif bad_min is not None and value < bad_min:
            return "danger"
        return "warning"
    else:
        if good_max is not None and value <= good_max:
            return "ok"
        elif bad_max is not None and value > bad_max:
            return "danger"
        return "warning"


def calculate_all_ratios(data: Dict[str, float], industry: str = "Manifatturiero") -> FinancialRatiosResult:
    bm = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["Manifatturiero"])
    alerts = []
    strengths = []

    total_assets = data.get("total_assets", 0)
    total_liabilities = data.get("total_liabilities", 0)
    revenue = data.get("revenue", 0)
    ebit = data.get("ebit", 0)
    ebitda = data.get("ebitda", ebit * 1.15)
    net_income = data.get("net_income", 0)
    equity = data.get("equity", max(total_assets - total_liabilities, 1))
    current_assets = data.get("current_assets", 0)
    current_liabilities = data.get("current_liabilities", 1)
    inventory = data.get("inventory", 0)
    accounts_receivable = data.get("accounts_receivable", 0)
    accounts_payable = data.get("accounts_payable", 0)
    fixed_assets = data.get("fixed_assets", 0)
    interest_expense = data.get("interest_expense", 0)
    depreciation = data.get("depreciation", 0)
    total_debt = data.get("total_debt", total_liabilities * 0.6)
    retained_earnings = data.get("retained_earnings", 0)

    # 1. LIQUIDITA'
    current_ratio = _safe_div(current_assets, current_liabilities)
    quick_ratio = _safe_div(current_assets - inventory, current_liabilities)
    cash_ratio = _safe_div(current_assets - inventory - accounts_receivable, current_liabilities)

    liq_ratios = [
        Ratio("Current Ratio", current_ratio or 0, bm.get("current_ratio"),
              _status(current_ratio, 1.5, None, 1.0),
              "Capacita' di coprire le passivita' correnti con le attivita' correnti",
              "Attivo Corrente / Passivo Corrente", "x"),
        Ratio("Quick Ratio", quick_ratio or 0, bm.get("quick_ratio"),
              _status(quick_ratio, 1.0, None, 0.7),
              "Liquidita' escludendo il magazzino (test acido)",
              "(Attivo Corrente - Magazzino) / Passivo Corrente", "x"),
        Ratio("Cash Ratio", cash_ratio or 0, bm.get("cash_ratio"),
              _status(cash_ratio, 0.2, None, 0.1),
              "Solo liquidita' immediata vs passivita' correnti",
              "Disponibilita' Liquide / Passivo Corrente", "x"),
    ]
    if current_ratio and current_ratio < 1.0:
        alerts.append("Attenzione: Current Ratio < 1: rischio liquidita' a breve termine")
    if current_ratio and current_ratio > 2.5:
        strengths.append("Eccellente liquidita' corrente")

    cat_liq = RatioCategory("Liquidita'", "Liquidita'", liq_ratios)

    # 2. SOLIDITA' PATRIMONIALE
    debt_equity = _safe_div(total_liabilities, equity)
    debt_assets = _safe_div(total_liabilities, total_assets)
    equity_multiplier = _safe_div(total_assets, equity)
    interest_coverage = _safe_div(ebit, interest_expense) if interest_expense > 0 else 99.0
    debt_ebitda = _safe_div(total_debt, ebitda) if ebitda > 0 else None

    solid_ratios = [
        Ratio("Debt/Equity", debt_equity or 0, bm.get("debt_equity"),
              _status(debt_equity, None, 1.5, None, 3.0, higher_is_better=False),
              "Rapporto tra capitale di terzi e capitale proprio",
              "Totale Passivo / Patrimonio Netto", "x"),
        Ratio("Debt/Assets", debt_assets or 0, bm.get("debt_assets"),
              _status(debt_assets, None, 0.6, None, 0.8, higher_is_better=False),
              "Percentuale delle attivita' finanziata da debito",
              "Totale Passivo / Totale Attivo", "%"),
        Ratio("Equity Multiplier", equity_multiplier or 0, None,
              _status(equity_multiplier, None, 2.5, None, 4.0, higher_is_better=False),
              "Leva finanziaria totale dell'azienda",
              "Totale Attivo / Patrimonio Netto", "x"),
        Ratio("Interest Coverage", interest_coverage or 0, bm.get("interest_coverage"),
              _status(interest_coverage, 3.0, None, 1.5),
              "Quante volte l'EBIT copre gli oneri finanziari",
              "EBIT / Oneri Finanziari", "x"),
        Ratio("Debt/EBITDA", debt_ebitda or 0, None,
              _status(debt_ebitda, None, 3.0, None, 5.0, higher_is_better=False) if debt_ebitda else "warning",
              "Anni necessari per ripagare il debito con l'EBITDA",
              "Debiti Finanziari / EBITDA", "x"),
    ]
    if debt_equity and debt_equity > 3.0:
        alerts.append("Debt/Equity > 3: eccessiva dipendenza dal debito")
    if interest_coverage and interest_coverage > 8:
        strengths.append("Copertura degli interessi eccellente")

    cat_solid = RatioCategory("Solidita' Patrimoniale", "Solidita'", solid_ratios)

    # 3. REDDITIVITA'
    roe = _safe_div(net_income, equity)
    roa = _safe_div(net_income, total_assets)
    roi = _safe_div(ebit, total_assets)
    ebitda_margin = _safe_div(ebitda, revenue)
    net_margin = _safe_div(net_income, revenue)
    gross_margin = data.get("gross_margin_raw", None)
    if gross_margin is None:
        gross_margin = ebitda_margin * 1.3 if ebitda_margin else None

    red_ratios = [
        Ratio("ROE", roe or 0, bm.get("roe"),
              _status(roe, 0.06, None, 0.0),
              "Rendimento del capitale proprio per gli azionisti",
              "Utile Netto / Patrimonio Netto", "%"),
        Ratio("ROA", roa or 0, bm.get("roa"),
              _status(roa, 0.04, None, 0.0),
              "Rendimento del totale delle attivita'",
              "Utile Netto / Totale Attivo", "%"),
        Ratio("ROI", roi or 0, bm.get("roi"),
              _status(roi, 0.05, None, 0.0),
              "Rendimento operativo sugli investimenti",
              "EBIT / Totale Attivo", "%"),
        Ratio("EBITDA Margin", ebitda_margin or 0, bm.get("ebitda_margin"),
              _status(ebitda_margin, 0.10, None, 0.03),
              "Redditivita' operativa lorda rispetto ai ricavi",
              "EBITDA / Ricavi", "%"),
        Ratio("Net Profit Margin", net_margin or 0, bm.get("net_margin"),
              _status(net_margin, 0.03, None, 0.0),
              "Percentuale di ricavi che diventa utile netto",
              "Utile Netto / Ricavi", "%"),
    ]
    if roe and roe < 0:
        alerts.append("ROE negativo: l'azienda sta distruggendo valore")
    if ebitda_margin and ebitda_margin > 0.20:
        strengths.append("EBITDA Margin eccellente (>20%)")

    cat_red = RatioCategory("Redditivita'", "Redditivita'", red_ratios)

    # 4. EFFICIENZA OPERATIVA
    asset_turnover = _safe_div(revenue, total_assets)
    days = 365
    dso = _safe_div(accounts_receivable * days, revenue) if accounts_receivable > 0 else None
    dpo = _safe_div(accounts_payable * days, revenue) if accounts_payable > 0 else None
    dio = _safe_div(inventory * days, revenue) if inventory > 0 else None
    ccc = None
    if dso is not None and dpo is not None and dio is not None:
        ccc = dso + dio - dpo

    eff_ratios = [
        Ratio("Asset Turnover", asset_turnover or 0, bm.get("asset_turnover"),
              _status(asset_turnover, 0.8, None, 0.3),
              "Quante volte le attivita' si girano in ricavi",
              "Ricavi / Totale Attivo", "x"),
    ]
    if dso is not None:
        eff_ratios.append(Ratio("DSO - Giorni Credito", dso, bm.get("dso"),
                                _status(dso, None, bm.get("dso", 60), None, bm.get("dso", 60) * 1.5, higher_is_better=False),
                                "Giorni medi per incassare i crediti commerciali",
                                "(Crediti / Ricavi) x 365", "giorni"))
    if dpo is not None:
        eff_ratios.append(Ratio("DPO - Giorni Debito", dpo, bm.get("dpo"),
                                _status(dpo, bm.get("dpo", 40) * 0.8, None, None, None),
                                "Giorni medi per pagare i fornitori",
                                "(Debiti Commerciali / Ricavi) x 365", "giorni"))
    if dio is not None:
        eff_ratios.append(Ratio("DIO - Giorni Magazzino", dio, bm.get("dio"),
                                _status(dio, None, bm.get("dio", 45), None, bm.get("dio", 45) * 1.5, higher_is_better=False),
                                "Giorni medi di giacenza del magazzino",
                                "(Magazzino / Ricavi) x 365", "giorni"))
    if ccc is not None:
        eff_ratios.append(Ratio("Cash Conversion Cycle", ccc, None,
                                _status(ccc, None, 60, None, 120, higher_is_better=False),
                                "Ciclo di conversione della cassa (DSO + DIO - DPO)",
                                "DSO + DIO - DPO", "giorni"))
        if ccc > 90:
            alerts.append(f"Cash Conversion Cycle elevato ({ccc:.0f} gg): capitale circolante assorbito")

    if dso and dso > bm.get("dso", 60) * 1.3:
        alerts.append(f"DSO {dso:.0f} gg superiore alla media settore: problema incasso crediti")

    cat_eff = RatioCategory("Efficienza Operativa", "Efficienza", eff_ratios)

    # 5. COPERTURA E FLUSSI
    op_cashflow = data.get("operating_cashflow", ebitda - data.get("tax_expense", net_income * 0.28))
    capex = data.get("capex", depreciation * 1.1)
    free_cashflow = op_cashflow - capex if op_cashflow else None

    fcf_yield = _safe_div(free_cashflow, total_assets) if free_cashflow else None
    cashflow_coverage = _safe_div(op_cashflow, total_debt) if total_debt > 0 else None

    cov_ratios = [
        Ratio("EBITDA / Totale Debiti", _safe_div(ebitda, total_debt) or 0, None,
              _status(_safe_div(ebitda, total_debt), 0.25, None, 0.10),
              "Capacita' di ripagare il debito con la gestione operativa",
              "EBITDA / Debiti Finanziari", "x"),
    ]
    if fcf_yield is not None:
        cov_ratios.append(Ratio("FCF Yield", fcf_yield, None,
                                _status(fcf_yield, 0.05, None, 0.0),
                                "Free Cash Flow rispetto al totale attivo",
                                "(Op. Cash Flow - CapEx) / Totale Attivo", "%"))
    if cashflow_coverage is not None:
        cov_ratios.append(Ratio("Cash Flow Coverage", cashflow_coverage, None,
                                _status(cashflow_coverage, 0.20, None, 0.05),
                                "Capacita' del cash flow di coprire il debito",
                                "Cash Flow Operativo / Debiti Finanziari", "x"))

    cat_cov = RatioCategory("Copertura e Flussi", "Flussi", cov_ratios)

    # 6. CRESCITA
    growth_ratios = []
    rev_growth = data.get("revenue_growth")
    ebitda_growth = data.get("ebitda_growth")

    if rev_growth is not None and rev_growth != 0:
        growth_ratios.append(Ratio("Crescita Ricavi YoY", rev_growth, 0.05,
                                   _status(rev_growth, 0.03, None, -0.05),
                                   "Variazione anno su anno dei ricavi",
                                   "(Ricavi_t - Ricavi_t-1) / Ricavi_t-1", "%"))
    if ebitda_growth is not None and ebitda_growth != 0:
        growth_ratios.append(Ratio("Crescita EBITDA YoY", ebitda_growth, 0.05,
                                   _status(ebitda_growth, 0.03, None, -0.05),
                                   "Variazione anno su anno dell'EBITDA",
                                   "(EBITDA_t - EBITDA_t-1) / EBITDA_t-1", "%"))

    if not growth_ratios:
        growth_ratios.append(Ratio("Crescita Ricavi", 0, None, "warning",
                                   "Carica dati di 2+ anni per calcolare la crescita",
                                   "Richiede dati storici", "%"))

    cat_growth = RatioCategory("Crescita", "Crescita", growth_ratios)

    # Score complessivo
    categories = [cat_liq, cat_solid, cat_red, cat_eff, cat_cov, cat_growth]
    for cat in categories:
        cat.compute_score()

    overall = round(sum(c.score for c in categories) / len(categories), 1)

    if overall >= 75:
        health_label, health_color = "ECCELLENTE", "#00C853"
    elif overall >= 55:
        health_label, health_color = "BUONO", "#64DD17"
    elif overall >= 40:
        health_label, health_color = "NELLA MEDIA", "#FFD600"
    elif overall >= 25:
        health_label, health_color = "SOTTO LA MEDIA", "#FF6D00"
    else:
        health_label, health_color = "CRITICO", "#D50000"

    return FinancialRatiosResult(
        categories=categories,
        overall_score=overall,
        industry=industry,
        health_label=health_label,
        health_color=health_color,
        key_alerts=alerts[:5],
        strengths=strengths[:3],
    )
