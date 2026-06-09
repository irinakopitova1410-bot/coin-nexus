"""
NEXUS Finance Pro — Cost Optimizer Engine
==========================================
Analisi costi dal bilancio: identifica quale costo sta affossando l'EBITDA,
calcola il potenziale di risparmio in €, suggerisce azioni concrete.
Confronto con benchmark PMI italiani per settore.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ─── Benchmark PMI Italiane (% sui ricavi) ────────────────────────────────────
COST_BENCHMARKS = {
    "Manifatturiero": {
        "cogs":        {"label": "Costo del Venduto (COGS)",        "benchmark": 0.62, "warning": 0.68, "danger": 0.75},
        "labor":       {"label": "Costo del Lavoro",                "benchmark": 0.18, "warning": 0.24, "danger": 0.30},
        "admin":       {"label": "Spese Generali e Amm.ve",         "benchmark": 0.06, "warning": 0.09, "danger": 0.13},
        "rent":        {"label": "Affitti e Leasing",               "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "finance":     {"label": "Oneri Finanziari",                "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "marketing":   {"label": "Marketing e Vendite",             "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "depreciation":{"label": "Ammortamenti e Sval.ni",         "benchmark": 0.03, "warning": 0.05, "danger": 0.07},
        "it":          {"label": "Costi IT e Tecnologia",           "benchmark": 0.01, "warning": 0.02, "danger": 0.04},
        "other":       {"label": "Altri Costi Operativi",           "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "ebitda_target": 0.12,
    },
    "Commercio": {
        "cogs":        {"label": "Costo del Venduto (COGS)",        "benchmark": 0.72, "warning": 0.77, "danger": 0.83},
        "labor":       {"label": "Costo del Lavoro",                "benchmark": 0.12, "warning": 0.16, "danger": 0.22},
        "admin":       {"label": "Spese Generali e Amm.ve",         "benchmark": 0.05, "warning": 0.08, "danger": 0.11},
        "rent":        {"label": "Affitti e Leasing",               "benchmark": 0.03, "warning": 0.05, "danger": 0.07},
        "finance":     {"label": "Oneri Finanziari",                "benchmark": 0.02, "warning": 0.04, "danger": 0.05},
        "marketing":   {"label": "Marketing e Vendite",             "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "depreciation":{"label": "Ammortamenti e Sval.ni",         "benchmark": 0.015,"warning": 0.03, "danger": 0.05},
        "it":          {"label": "Costi IT e Tecnologia",           "benchmark": 0.008,"warning": 0.015,"danger": 0.03},
        "other":       {"label": "Altri Costi Operativi",           "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "ebitda_target": 0.06,
    },
    "Servizi": {
        "cogs":        {"label": "Costo Erogazione Servizio",       "benchmark": 0.35, "warning": 0.42, "danger": 0.50},
        "labor":       {"label": "Costo del Lavoro",                "benchmark": 0.45, "warning": 0.52, "danger": 0.60},
        "admin":       {"label": "Spese Generali e Amm.ve",         "benchmark": 0.08, "warning": 0.12, "danger": 0.16},
        "rent":        {"label": "Affitti e Leasing",               "benchmark": 0.05, "warning": 0.08, "danger": 0.11},
        "finance":     {"label": "Oneri Finanziari",                "benchmark": 0.015,"warning": 0.03, "danger": 0.05},
        "marketing":   {"label": "Marketing e Vendite",             "benchmark": 0.03, "warning": 0.05, "danger": 0.08},
        "depreciation":{"label": "Ammortamenti e Sval.ni",         "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "it":          {"label": "Costi IT e Tecnologia",           "benchmark": 0.02, "warning": 0.04, "danger": 0.07},
        "other":       {"label": "Altri Costi Operativi",           "benchmark": 0.015,"warning": 0.03, "danger": 0.05},
        "ebitda_target": 0.18,
    },
    "Costruzioni": {
        "cogs":        {"label": "Costo Lavori e Subappalti",       "benchmark": 0.68, "warning": 0.74, "danger": 0.80},
        "labor":       {"label": "Costo del Lavoro Diretto",        "benchmark": 0.16, "warning": 0.21, "danger": 0.27},
        "admin":       {"label": "Spese Generali e Amm.ve",         "benchmark": 0.06, "warning": 0.09, "danger": 0.12},
        "rent":        {"label": "Noleggio Mezzi e Attrezzature",   "benchmark": 0.01, "warning": 0.03, "danger": 0.05},
        "finance":     {"label": "Oneri Finanziari",                "benchmark": 0.03, "warning": 0.05, "danger": 0.07},
        "marketing":   {"label": "Marketing e Commerciale",         "benchmark": 0.01, "warning": 0.02, "danger": 0.04},
        "depreciation":{"label": "Ammortamenti e Sval.ni",         "benchmark": 0.025,"warning": 0.045,"danger": 0.06},
        "it":          {"label": "Costi IT e Software Gestionale",  "benchmark": 0.005,"warning": 0.01, "danger": 0.02},
        "other":       {"label": "Altri Costi Operativi",           "benchmark": 0.025,"warning": 0.04, "danger": 0.06},
        "ebitda_target": 0.08,
    },
    "Tecnologia": {
        "cogs":        {"label": "Costo Sviluppo e Prodotto",       "benchmark": 0.30, "warning": 0.38, "danger": 0.48},
        "labor":       {"label": "Costo del Lavoro (R&D + Sales)",  "benchmark": 0.50, "warning": 0.58, "danger": 0.66},
        "admin":       {"label": "Spese Generali e Amm.ve",         "benchmark": 0.08, "warning": 0.12, "danger": 0.16},
        "rent":        {"label": "Affitti e Cloud Infrastructure",  "benchmark": 0.03, "warning": 0.05, "danger": 0.08},
        "finance":     {"label": "Oneri Finanziari",                "benchmark": 0.01, "warning": 0.025,"danger": 0.04},
        "marketing":   {"label": "Marketing, Sales e CAC",          "benchmark": 0.08, "warning": 0.13, "danger": 0.18},
        "depreciation":{"label": "Ammortamenti e Sval.ni",         "benchmark": 0.02, "warning": 0.04, "danger": 0.06},
        "it":          {"label": "Infrastruttura IT e Licenze",     "benchmark": 0.03, "warning": 0.05, "danger": 0.08},
        "other":       {"label": "Altri Costi Operativi",           "benchmark": 0.01, "warning": 0.025,"danger": 0.04},
        "ebitda_target": 0.25,
    },
}

# Azioni suggerite per ogni voce di costo
COST_ACTIONS = {
    "cogs": [
        "🔄 Rinegoziare contratti fornitori (target: -5-10% sul prezzo di acquisto)",
        "📦 Ottimizzare la gestione del magazzino e ridurre gli scarti",
        "🏭 Valutare fornitori alternativi o home sourcing per componenti chiave",
        "⚡ Migliorare l'efficienza produttiva e ridurre i tempi di lavorazione",
        "📊 Implementare make-or-buy analysis per ogni linea di prodotto",
    ],
    "labor": [
        "🤖 Automazione di processi ripetitivi (ROI medio 18-24 mesi)",
        "📅 Ottimizzare i turni e ridurre gli straordinari non pianificati",
        "📋 Welfare aziendale: riduce il turnover del 30% (risparmio su formazione)",
        "🎯 Revisione dell'organizzazione: eliminare ridondanze strutturali",
        "📈 Sistema incentivante legato alla produttività (salary-for-performance)",
    ],
    "admin": [
        "📋 Outsourcing di funzioni non core (contabilità, HR amministrativo)",
        "💻 Digitalizzazione processi: riduce i costi admin del 25-40%",
        "✂️ Riduzione carta e archiviazione fisica → archivio digitale",
        "🔍 Audit spese: eliminare abbonamenti e servizi non utilizzati",
        "🏢 Razionalizzare gli spazi ufficio (smart working ibrido)",
    ],
    "rent": [
        "🤝 Rinegoziare i contratti di locazione (mercato favorevole agli inquilini)",
        "💼 Smart working parziale → riduzione superficie necessaria",
        "📦 Ottimizzare i magazzini: layout Lean, riduzione giacenze",
        "🔄 Valutare sale-and-leaseback per immobili di proprietà",
        "📍 Consolidare sedi: unire uffici multipli in un'unica location",
    ],
    "finance": [
        "🏦 Rifinanziare i debiti a tassi più bassi (spread attuale mercato: -0.5-1%)",
        "💳 Migliorare la gestione della tesoreria (riduce fabbisogno finanziario)",
        "📉 Ridurre il debito netto con la liquidità non impiegata",
        "🔄 Factoring pro-soluto per anticipare i crediti commerciali",
        "📊 Ristrutturazione del debito: allungare le scadenze, ridurre le rate",
    ],
    "marketing": [
        "🎯 Marketing automation: stessa efficacia a costi -30-40%",
        "📊 Analisi CAC/LTV per eliminare i canali non profittevoli",
        "🤝 Programma referral: costo acquisizione 5x inferiore alla pubblicità",
        "📱 Spostare budget da media tradizionali a digital (ROI misurabile)",
        "🔍 SEO organico: investimento una tantum vs costo continuo ads",
    ],
    "depreciation": [
        "📊 Revisione vita utile dei cespiti (potrebbe ridurre le quote)",
        "♻️ Dismissione cespiti obsoleti e inutilizzati",
        "🔄 Leasing operativo vs acquisto: analisi make-or-buy aggiornata",
        "💡 Incentivi fiscali: Piano Transizione 5.0 (credito imposta 35-45%)",
        "📋 Perizia tecnica indipendente per verifica correttezza ammortamenti",
    ],
    "it": [
        "☁️ Migrazione cloud: da CAPEX a OPEX, riduzione costi -20-35%",
        "🔍 Software audit: eliminare licenze non utilizzate o duplicate",
        "🤝 Consolidare i vendor IT: da 10+ fornitori a 2-3 partner strategici",
        "🛡️ Open source alternatives per software non-core",
        "📊 IT chargeback: rende visibili i costi IT per business unit",
    ],
    "other": [
        "🔍 Audit completo delle spese 'altri costi': classificazione precisa",
        "✂️ Eliminare spese discrezionali non correlate al business",
        "📋 Policy spese aziendali con limiti e pre-approvazioni",
        "🔄 Centralizzare gli acquisti per ottenere sconti volume",
        "📊 Analisi Pareto: il 20% delle voci genera l'80% del costo",
    ],
}


@dataclass
class CostItem:
    key: str
    label: str
    value_eur: float           # valore assoluto in €
    pct_revenue: float         # % sui ricavi (azienda)
    benchmark_pct: float       # % benchmark settore
    warning_pct: float
    danger_pct: float
    status: str                # "ok" | "warning" | "danger"
    gap_pct: float             # differenza vs benchmark (positivo = troppo alto)
    gap_eur: float             # gap in € (risparmio potenziale)
    impact_on_ebitda: float    # punti % che migliora l'EBITDA se si allinea
    priority_rank: int         # 1 = problema più grave
    actions: List[str]
    quick_win: str             # azione singola più rapida


@dataclass
class CostOptimizerResult:
    revenue: float
    current_ebitda_pct: float
    target_ebitda_pct: float
    industry: str
    items: List[CostItem]              # ordinati per priorità
    total_savings_eur: float           # risparmio totale potenziale
    ebitda_after_fix: float            # EBITDA % dopo fix
    top_problem: CostItem              # il problema principale
    quick_wins: List[CostItem]         # top 3 fix rapidi
    risk_level: str                    # "alto" | "medio" | "basso"
    summary: str                       # testo sintetico
    waterfall: List[Dict]              # dati per waterfall chart
    simulation_base: Dict              # dati per simulatore


def analyze_costs(
    revenue: float,
    costs: Dict[str, float],       # {"cogs": 500000, "labor": 200000, ...}
    industry: str = "Manifatturiero",
    current_ebitda: Optional[float] = None,
) -> CostOptimizerResult:
    """
    Analizza i costi dal conto economico e identifica le voci critiche.
    
    revenue: Ricavi netti
    costs: Dizionario con le voci di costo in €
    industry: Settore dell'azienda
    current_ebitda: EBITDA attuale in € (se noto)
    """
    bm = COST_BENCHMARKS.get(industry, COST_BENCHMARKS["Manifatturiero"])
    ebitda_target = bm["ebitda_target"]
    
    # EBITDA attuale
    total_costs = sum(v for k, v in costs.items() if k != "ebitda_target")
    if current_ebitda is None:
        current_ebitda = revenue - total_costs
    current_ebitda_pct = current_ebitda / revenue if revenue > 0 else 0
    
    items_raw = []
    total_savings = 0.0
    
    for key, cost_def in bm.items():
        if key == "ebitda_target":
            continue
        
        value_eur = costs.get(key, 0.0)
        if value_eur <= 0:
            continue
        
        pct = value_eur / revenue if revenue > 0 else 0
        bench = cost_def["benchmark"]
        warn = cost_def["warning"]
        dang = cost_def["danger"]
        
        if pct <= bench * 1.05:
            status = "ok"
        elif pct <= warn:
            status = "warning"
        else:
            status = "danger"
        
        gap_pct = max(0.0, pct - bench)
        gap_eur = gap_pct * revenue
        
        # Risparmio raggiungibile: portarsi al benchmark
        savings = gap_eur
        total_savings += savings
        
        # Impatto sull'EBITDA
        impact = gap_pct  # ogni punto % di risparmio = punto % di EBITDA
        
        items_raw.append({
            "key": key,
            "label": cost_def["label"],
            "value_eur": value_eur,
            "pct_revenue": pct,
            "benchmark_pct": bench,
            "warning_pct": warn,
            "danger_pct": dang,
            "status": status,
            "gap_pct": gap_pct,
            "gap_eur": gap_eur,
            "impact_on_ebitda": impact,
            "actions": COST_ACTIONS.get(key, []),
            "quick_win": COST_ACTIONS.get(key, ["Analisi dettagliata necessaria"])[0],
        })
    
    # Ordina per impatto (gap_eur decrescente) → priority_rank
    items_raw.sort(key=lambda x: x["gap_eur"], reverse=True)
    
    items = []
    for i, r in enumerate(items_raw):
        items.append(CostItem(
            key=r["key"],
            label=r["label"],
            value_eur=r["value_eur"],
            pct_revenue=r["pct_revenue"],
            benchmark_pct=r["benchmark_pct"],
            warning_pct=r["warning_pct"],
            danger_pct=r["danger_pct"],
            status=r["status"],
            gap_pct=r["gap_pct"],
            gap_eur=r["gap_eur"],
            impact_on_ebitda=r["impact_on_ebitda"],
            priority_rank=i + 1,
            actions=r["actions"],
            quick_win=r["quick_win"],
        ))
    
    ebitda_after = current_ebitda_pct + (total_savings / revenue if revenue > 0 else 0)
    
    # Risk level
    danger_count = sum(1 for it in items if it.status == "danger")
    warning_count = sum(1 for it in items if it.status == "warning")
    if danger_count >= 2 or current_ebitda_pct < 0.02:
        risk_level = "ALTO"
    elif danger_count >= 1 or warning_count >= 2:
        risk_level = "MEDIO"
    else:
        risk_level = "BASSO"
    
    top = items[0] if items else None
    quick_wins = [it for it in items if it.status in ("danger", "warning")][:3]
    
    # Summary
    if top and top.gap_eur > 0:
        summary = (
            f"Il problema principale è **{top.label}** che incide per "
            f"{top.pct_revenue*100:.1f}% sui ricavi vs benchmark settore "
            f"{top.benchmark_pct*100:.1f}%. Ottimizzando questo costo puoi "
            f"risparmiare **€{top.gap_eur:,.0f}/anno** e portare l'EBITDA da "
            f"{current_ebitda_pct*100:.1f}% a {(current_ebitda_pct+top.impact_on_ebitda)*100:.1f}%."
        )
    else:
        summary = "✅ I costi aziendali sono allineati ai benchmark di settore. Struttura dei costi efficiente."
    
    # Waterfall data
    waterfall = [{"label": "📈 Ricavi", "value": revenue, "type": "total"}]
    for it in sorted(items, key=lambda x: x.value_eur, reverse=True):
        waterfall.append({
            "label": it.label,
            "value": -it.value_eur,
            "type": "danger" if it.status == "danger" else ("warning" if it.status == "warning" else "ok"),
            "benchmark_value": -it.benchmark_pct * revenue,
        })
    waterfall.append({"label": "💰 EBITDA", "value": current_ebitda, "type": "ebitda"})
    
    # Simulation base: dict con % attuali per sliders
    simulation_base = {
        it.key: {
            "current_pct": it.pct_revenue,
            "benchmark_pct": it.benchmark_pct,
            "label": it.label,
            "value_eur": it.value_eur,
        }
        for it in items
    }
    
    return CostOptimizerResult(
        revenue=revenue,
        current_ebitda_pct=current_ebitda_pct,
        target_ebitda_pct=ebitda_target,
        industry=industry,
        items=items,
        total_savings_eur=total_savings,
        ebitda_after_fix=min(ebitda_after, 0.50),  # cap realistico
        top_problem=top,
        quick_wins=quick_wins,
        risk_level=risk_level,
        summary=summary,
        waterfall=waterfall,
        simulation_base=simulation_base,
    )


def simulate_cost_reduction(
    result: CostOptimizerResult,
    reductions: Dict[str, float],  # {"labor": 0.10} = riduzione 10%
) -> Dict:
    """
    Simula l'impatto di una riduzione dei costi sull'EBITDA e sul rating.
    reductions: {"key": pct_reduction} dove pct_reduction è 0-1
    """
    revenue = result.revenue
    total_savings = 0.0
    details = []
    
    for item in result.items:
        reduction = reductions.get(item.key, 0.0)
        if reduction > 0:
            saving = item.value_eur * reduction
            total_savings += saving
            details.append({
                "label": item.label,
                "saving_eur": saving,
                "new_pct": item.pct_revenue * (1 - reduction),
                "benchmark_pct": item.benchmark_pct,
            })
    
    new_ebitda_pct = result.current_ebitda_pct + (total_savings / revenue if revenue > 0 else 0)
    new_ebitda_eur = new_ebitda_pct * revenue
    
    # Stima impatto sul credito (EBITDA × 3 = capacità di indebitamento)
    loan_capacity_before = result.current_ebitda_pct * revenue * 3
    loan_capacity_after = new_ebitda_pct * revenue * 3
    
    # Rating semplificato
    if new_ebitda_pct >= 0.20:
        rating = "AAA"
    elif new_ebitda_pct >= 0.15:
        rating = "AA"
    elif new_ebitda_pct >= 0.10:
        rating = "A"
    elif new_ebitda_pct >= 0.07:
        rating = "BBB"
    elif new_ebitda_pct >= 0.04:
        rating = "BB"
    elif new_ebitda_pct >= 0.02:
        rating = "B"
    else:
        rating = "CCC"
    
    return {
        "total_savings_eur": total_savings,
        "new_ebitda_pct": new_ebitda_pct,
        "new_ebitda_eur": new_ebitda_eur,
        "loan_capacity_before": loan_capacity_before,
        "loan_capacity_after": loan_capacity_after,
        "new_rating": rating,
        "details": details,
    }
