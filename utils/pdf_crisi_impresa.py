"""Informational financial indicators, not a legal diagnosis or certification.

Thresholds are internal screening conventions, not universal statutory limits.
Missing inputs are not estimates and do not imply a healthy financial position.
"""
import datetime
import math

from fpdf import XPos, YPos
from utils.pdf_export import (
    clean_text, NexusPDF, PRIMARY, DANGER, WARNING, SUCCESS, GRAY, DARK_TEXT,
)


# Internal screening assumptions, not statutory sector thresholds.
SOGLIE_OF_RICAVI = {
    "agricoltura": 0.06, "commercio": 0.04, "costruzioni": 0.07,
    "manifatturiero": 0.05, "servizi": 0.06, "holding": 0.04, "altro": 0.06,
}


def calcola_indici_ccii(data: dict, settore: str = "altro") -> dict:
    """Calculate screening ratios using supplied, finite inputs only.

    DSCR requires operating_cashflow and debt_service for the same period;
    EBITDA is not cash flow and debt principal cannot be inferred from balances.
    ``None``/``unavailable`` denotes an undefined or missing ratio.
    """
    def number(*keys):
        for key in keys:
            if data.get(key) is not None:
                try:
                    value = float(data[key])
                except (TypeError, ValueError, OverflowError):
                    return None
                return value if math.isfinite(value) else None
        return None

    def ratio(numerator, denominator):
        if numerator is None or denominator is None or denominator <= 0:
            return None
        value = numerator / denominator
        return value if math.isfinite(value) else None

    assets = number("total_assets", "totale_attivo")
    equity = number("equity", "patrimonio_netto")
    current_assets = number("current_assets", "attivo_corrente")
    current_liabilities = number("current_liabilities", "passivo_corrente")
    revenue = number("revenue", "ricavi_netti", "fatturato")
    interest = number("interest_expense", "oneri_finanziari")
    debt = number("total_debt", "debiti_finanziari", "totale_debiti")
    ebitda = number("ebitda")
    # Preserve an explicitly reported zero; derive only genuinely absent EBITDA.
    if data.get("ebitda") is None:
        ebit = number("ebit")
        depreciation = number("depreciation", "ammortamenti")
        if ebit is not None and depreciation is not None:
            ebitda = ebit + depreciation
    operating_cf = number("operating_cashflow")
    debt_service = number("debt_service")
    results = {}

    def add(key, name, formula, value, threshold, status, note, percent=False):
        item = {
            "nome": name, "formula": formula,
            "valore": round(value, 4) if value is not None else None,
            "soglia": threshold, "stato": status if value is not None else "unavailable",
            "note": note if value is not None else (
                "N/D: dati mancanti, non finiti o denominatore non positivo. "
                "Nessuna stima sostitutiva; verificare i dati e il periodo di riferimento."
            ),
            "riferimento": "Criterio interno di analisi finanziaria; non soglia di legge",
        }
        if percent:
            item["valore_pct"] = f"{value * 100:.2f}%" if value is not None else "N/D"
        results[key] = item

    def lower_status(value, good, caution):
        return "unavailable" if value is None else (
            "ok" if value >= good else "warning" if value >= caution else "danger"
        )

    def upper_status(value, good, caution):
        return "unavailable" if value is None else (
            "ok" if value <= good else "warning" if value <= caution else "danger"
        )

    dscr = ratio(operating_cf, debt_service)
    add("dscr", "DSCR (Debt Service Coverage Ratio)",
        "Cash Flow Operativo / Servizio del Debito dello stesso periodo", dscr,
        ">= 1.0", lower_status(dscr, 1, 0.8),
        "Confronto tra cassa operativa e servizio del debito forniti. "
        "Verificare disponibilita' della cassa per il debito e coerenza temporale; non e' una previsione.")
    of = ratio(interest, revenue)
    limit = SOGLIE_OF_RICAVI.get(settore.lower(), 0.06)
    add("of_ricavi", "Oneri Finanziari / Ricavi", "Oneri Finanziari / Ricavi netti",
        of, f"<= {limit * 100:.0f}% (ipotesi interna, settore: {settore})",
        upper_status(of, limit, limit * 1.5), "Incidenza degli oneri sui ricavi dichiarati.", True)
    eq = ratio(equity, assets)
    add("adeguatezza_patrimoniale", "Patrimonio Netto / Attivo",
        "Patrimonio Netto / Totale Attivo", eq, ">= 8%",
        "danger" if equity is not None and equity < 0 else lower_status(eq, 0.08, 0),
        "Indicatore patrimoniale; eventuali perdite richiedono una valutazione professionale specifica.", True)
    cash_return = ratio(operating_cf, assets)
    add("ritorno_liquido_attivo", "Ritorno Liquido dell'Attivo",
        "Cash Flow Operativo / Totale Attivo", cash_return, ">= 0%",
        lower_status(cash_return, 0, -0.05), "Rendimento di cassa sui valori forniti.", True)
    liquidity = ratio(current_assets, current_liabilities)
    add("liquidita", "Indice di Liquidita' (Current Ratio)",
        "Attivo Corrente / Passivo Corrente", liquidity, ">= 1.0",
        lower_status(liquidity, 1, 0.8), "Rapporto contabile; non prova la liquidabilita' degli attivi.")
    # Keep the legacy dictionary key for callers; total_debt is NOT net debt (PFN).
    leverage = ratio(debt, ebitda)
    add("pfn_ebitda", "Debito dichiarato / EBITDA", "Debito dichiarato / EBITDA",
        leverage, "<= 4x (attenzione fino a 6x)", upper_status(leverage, 4, 6),
        "Il debito fornito non e' automaticamente PFN: non viene sottratta cassa non dichiarata.")
    if debt is not None and debt > 0 and ebitda is not None and ebitda <= 0:
        # Undefined multiple, but a known adverse operating/debt combination.
        results["pfn_ebitda"]["stato"] = "danger"
        results["pfn_ebitda"]["note"] = (
            "N/D: multiplo non significativo con EBITDA non positivo e debito positivo. "
            "Condizione finanziaria da approfondire; non diagnosi di insolvenza."
        )
    coverage = ratio(ebitda, interest)
    add("interest_coverage", "Coverage Oneri Finanziari (EBITDA/OF)",
        "EBITDA / Oneri Finanziari", coverage, ">= 2x", lower_status(coverage, 2, 1),
        "Copertura economica degli interessi, distinta dalla copertura monetaria del debito.")

    counts = {status: sum(v["stato"] == status for v in results.values())
              for status in ("ok", "warning", "danger", "unavailable")}
    if counts["danger"] >= 3 or (equity is not None and equity < 0):
        judgement, state = "INDICATORI FINANZIARI CRITICI", "danger"
    elif counts["danger"] or counts["warning"] >= 3:
        judgement, state = "INDICATORI DA APPROFONDIRE", "warning"
    elif counts["unavailable"]:
        judgement, state = "ANALISI PARZIALE - DATI INCOMPLETI", "warning"
    else:
        judgement, state = "INDICATORI ENTRO LE SOGLIE INTERNE", "ok"
    results["_meta"] = {
        "giudizio": judgement, "giudizio_stato": state,
        "giudizio_desc": (
            "Screening finanziario su soglie interne, non diagnosi di crisi o insolvenza. "
            "I dati mancanti non indicano assenza di rischio. Il risultato non determina "
            "obblighi, procedure o termini legali e richiede verifica di un professionista abilitato."
        ),
        "danger_count": counts["danger"], "warning_count": counts["warning"],
        "ok_count": counts["ok"], "unavailable_count": counts["unavailable"],
        "settore": settore,
        "data_analisi": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    return results


def generate_crisi_impresa_report(
    company_name: str,
    data: dict,
    settore: str = "altro",
    revisore: str = "",
    user_name: str = "NEXUS Finance Pro",
) -> bytes:
    """Generate an informational financial screening PDF; no certification."""
    indici = calcola_indici_ccii(data, settore)
    meta = indici.pop("_meta")
    pdf = NexusPDF(company_name=company_name, report_type="Indicatori finanziari")
    pdf.add_page()
    colors = {"ok": SUCCESS, "warning": WARNING, "danger": DANGER, "unavailable": GRAY}

    def paragraph(text, bold=False):
        pdf.set_font("Helvetica", "B" if bold else "", 9)
        pdf.set_text_color(*DARK_TEXT)
        pdf.multi_cell(0, 5, clean_text(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    pdf.section_title("SCREENING DEGLI INDICATORI FINANZIARI")
    paragraph(company_name, True)
    paragraph(f"Analisi del {meta['data_analisi']} | Settore: {settore} | Elaborata da: {user_name}")
    paragraph(meta["giudizio"], True)
    paragraph(meta["giudizio_desc"])
    paragraph(f"Indicatori critici: {meta['danger_count']} | Da approfondire: {meta['warning_count']} | "
              f"Entro soglie: {meta['ok_count']} | N/D: {meta['unavailable_count']}")
    paragraph("Le soglie riportate sono ipotesi interne di screening, non limiti normativi universali. "
              "La loro appropriatezza dipende da settore, scadenze, contratti e situazione aziendale.")
    for indice in indici.values():
        if pdf.get_y() > 225:
            pdf.add_page()
        pdf.set_fill_color(*colors[indice["stato"]])
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.multi_cell(0, 6, clean_text(indice["nome"]), fill=True,
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        value = "N/D" if indice["valore"] is None else indice.get("valore_pct", str(indice["valore"]))
        paragraph(f"Formula: {indice['formula']}\nValore: {value}\nSoglia interna: {indice['soglia']}")
        paragraph(indice["note"])

    pdf.section_title("LIMITI E VERIFICA PROFESSIONALE")
    paragraph("Documento informativo basato sui dati forniti dall'utente, non verificati. "
              "Non costituisce parere legale, attestazione, revisione o certificazione. "
              "Non accerta crisi o insolvenza e non prescrive l'accesso a procedure. "
              "La verifica di eventuali obblighi e strumenti applicabili spetta a professionisti "
              "abilitati sulla base della normativa vigente e del caso concreto.")
    paragraph("Approfondimenti suggeriti: riconciliare i dati con il bilancio e le scadenze; "
              "acquisire flussi di cassa e servizio del debito coerenti per periodo; "
              "valutare con un professionista continuita' aziendale, liquidita' prospettica e sostenibilita' del debito.")
    if revisore:
        paragraph(f"Referente indicato dall'utente (non attestazione): {revisore}")
    return bytes(pdf.output())
