"""Descriptive balance diagnostics from observed values only.

No model score, cash-flow estimate, credit offer, network call or database write.
An absent value remains absent; an explicit zero remains zero.
"""
import math
from numbers import Real


def format_amount(value, unit="EUR", digits=2):
    if value is None:
        return "N/D"
    text = f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{text} {unit}".strip()


def analyze_available_balance(data, source=None):
    """Compute only ratios whose full inputs are known and meaningful."""
    source = source or {}
    known = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError(f"Dato non numerico o non finito: {key}")
        known[key] = float(value)

    ratios = []

    def ratio(code, label, numerator, denominator, multiplier, unit, formula):
        missing = [field for field in (numerator, denominator) if field not in known]
        if missing:
            value, reason = None, "Dato da integrare: " + ", ".join(missing)
        elif known[denominator] <= 0:
            value, reason = None, "Non significativo con denominatore nullo o negativo."
        else:
            value = known[numerator] / known[denominator] * multiplier
            reason = formula
        ratios.append({"code": code, "label": label, "value": value, "unit": unit, "reason": reason})

    ratio("ebit_margin", "Margine operativo (EBIT)", "ebit", "fatturato", 100, "%", "EBIT / ricavi × 100")
    ratio("ebitda_margin", "Margine EBITDA", "ebitda", "fatturato", 100, "%", "EBITDA / ricavi × 100")
    ratio("equity_ratio", "Patrimonio netto / attivo", "patrimonio_netto", "totale_attivo", 100, "%", "Patrimonio netto / totale attivo × 100")
    ratio("current_ratio", "Liquidità corrente", "attivo_corrente", "passivo_corrente", 1, "x", "Attivo corrente / passività correnti")
    ratio("debt_ebitda", "Debiti finanziari / EBITDA", "debiti_finanziari", "ebitda", 1, "x", "Debiti finanziari complessivi / EBITDA positivo")
    previous = known.get("fatturato_prev")
    growth = ((known["fatturato"] - previous) / previous * 100
              if "fatturato" in known and previous is not None and previous > 0 else None)
    ratios.append({"code": "revenue_growth", "label": "Variazione ricavi", "value": growth, "unit": "%",
                   "reason": "(Ricavi attuali − ricavi precedenti) / ricavi precedenti × 100"
                   if growth is not None else "Richiede ricavi del periodo precedente positivi e ricavi attuali."})
    ratios.append({"code": "dscr", "label": "DSCR prospettico", "value": None, "unit": "x",
                   "reason": "N/D: occorrono flussi disponibili per il debito e servizio del debito sullo stesso orizzonte prospettico. Il solo bilancio SP/CE non basta."})

    signals, actions = [], []
    if known.get("patrimonio_netto", 0) < 0:
        signals.append("Patrimonio netto negativo: il prospetto evidenzia uno squilibrio patrimoniale.")
        actions.append("Verificare patrimonio e continuità aziendale con l’amministrazione e i professionisti incaricati; valutare gli interventi necessari sulla base della situazione aggiornata.")
    if known.get("ebit", 0) < 0:
        signals.append("Risultato operativo negativo: i costi operativi complessivi superano il valore della produzione.")
        actions.append("Riconciliare ricavi e costi per individuare le cause della perdita operativa, senza assumere tagli o risparmi non documentati.")
    if known.get("ebitda", 0) < 0:
        signals.append("EBITDA negativo. Non equivale al cash flow: il flusso di cassa richiede il rendiconto finanziario.")
    if known.get("utile_netto", 0) < 0:
        signals.append("Il periodo si chiude con una perdita netta.")
    if growth is not None and growth < 0:
        signals.append(f"Ricavi in diminuzione del {format_amount(abs(growth), '%')} rispetto al periodo di confronto.")
    if known.get("cash_operativo", 0) < 0:
        signals.append("Il flusso di cassa operativo fornito è negativo.")
    if "passivo_corrente" in known and known["passivo_corrente"] > 0 and "attivo_corrente" in known:
        if known["attivo_corrente"] < known["passivo_corrente"]:
            signals.append("Le passività correnti superano l’attivo corrente. Verificare scadenze e liquidità disponibile.")
    if "passivo_corrente" not in known or "cash_operativo" not in known:
        actions.append("Integrare scadenzario e rendiconto finanziario per valutare liquidità e flussi di cassa; non ricavarli dalla sola liquidità in banca.")

    reported = source.get("_reported_ebitda")
    reconciliation = None
    if reported is not None and "ebitda" in known:
        reconciliation = {
            "derived": known["ebitda"], "reported": float(reported),
            "difference": float(reported) - known["ebitda"],
        }
    source_issues = [str(note) for note in source.get("_import_warnings", [])
                     if str(note).startswith("ATTENZIONE:")]
    return {"values": known, "ratios": ratios, "signals": signals, "actions": actions,
            "source_issues": source_issues, "reconciliation": reconciliation,
            "period": source.get("_source_period"), "comparison_period": source.get("_comparison_period"),
            "ebitda_derived": source.get("_source_format") == "civil_balance",
            "credit_score": None, "estimated_credit": None}


def diagnostic_text(report, company, missing_labels=()):
    """Real export of the current descriptive result, not a placeholder button."""
    lines = ["NEXUS — ANALISI DESCRITTIVA DEL BILANCIO", str(company),
             "Periodo: " + str(report.get("period") or "non indicato"), "",
             "Calcoli sui dati disponibili; non è un rating bancario o una delibera di credito.", ""]
    labels = {"fatturato": "Ricavi", "ebit": "EBIT", "ebitda": "EBITDA",
              "patrimonio_netto": "Patrimonio netto", "utile_netto": "Utile/perdita",
              "cash_corrente": "Disponibilità liquide", "totale_attivo": "Totale attivo"}
    lines += [label + ": " + format_amount(report["values"].get(key)) for key, label in labels.items()]
    lines += ["", "INDICATORI"]
    lines += [row["label"] + ": " + format_amount(row["value"], row["unit"]) + " — " + row["reason"]
              for row in report["ratios"]]
    lines += ["", "EVIDENZE"] + (report["signals"] or ["Nessuna delle criticità controllate nei dati disponibili. Non è una conferma di solvibilità."])
    lines += ["", "PASSI SUCCESSIVI"] + report["actions"]
    if report["reconciliation"]:
        r = report["reconciliation"]
        lines += ["", "EBITDA DA RICONCILIARE", "Derivato: " + format_amount(r["derived"]),
                  "Riportato nel file: " + format_amount(r["reported"]),
                  "Differenza: " + format_amount(r["difference"])]
    if source_issues := report["source_issues"]:
        lines += ["", "CONTROLLI DEL PROSPETTO"] + source_issues
    if missing_labels:
        lines += ["", "DATI DA INTEGRARE PER IL MODELLO COMPLETO"] + list(missing_labels)
    lines += ["", "Credit Score e credito ottenibile: N/D in questa sintesi descrittiva.",
              "Un dato mancante non equivale a zero. Nessuna analisi è salvata automaticamente da questo export."]
    return "\n".join(lines).encode("utf-8")
