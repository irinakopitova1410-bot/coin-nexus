"""
NEXUS Finance Pro — Report "Crisi d'Impresa" (D.Lgs. 14/2019 CCII)
Documento legalmente rilevante: calcola gli indici di allerta CNDCEC,
DSCR, patrimonio netto e PFN/EBITDA secondo le soglie di legge.

Riferimenti normativi:
  - D.Lgs. 14/2019 - Codice della Crisi d'Impresa e dell'Insolvenza (CCII)
  - D.Lgs. 83/2022 - Aggiornamento CCII (recepimento Direttiva UE 2019/1023)
  - D.L. 118/2021 - Composizione Negoziata della Crisi
  - CNDCEC - Indici di allerta (luglio 2019)
  - OIC 6 - Ristrutturazione del debito
"""
from fpdf import FPDF, XPos, YPos
import datetime
import io
from typing import Dict, Optional
from utils.pdf_export import clean_text, NexusPDF, PRIMARY, ACCENT, DANGER, WARNING, SUCCESS, GRAY, WHITE, DARK_TEXT, LIGHT_BG


# ─── Soglie legali CNDCEC per settore ────────────────────────────────────────
# (Oneri Finanziari / Ricavi) massima tolleranza per settore
SOGLIE_OF_RICAVI = {
    "agricoltura":      0.06,
    "commercio":        0.04,
    "costruzioni":      0.07,
    "manifatturiero":   0.05,
    "servizi":          0.06,
    "holding":          0.04,
    "altro":            0.06,
}


def calcola_indici_ccii(data: dict, settore: str = "altro") -> dict:
    """
    Calcola tutti gli indici di allerta richiesti dal CCII / CNDCEC.

    Input `data` (valori in euro):
        total_assets, equity, current_assets, current_liabilities,
        revenue, ebitda, ebit, net_income, interest_expense,
        total_debt, depreciation, working_capital,
        operating_cashflow (opzionale), debt_service (opzionale)

    Returns: dict con ogni indice, valore, soglia, stato (ok/warning/danger)
    """
    g = lambda k, d=0.0: float(data.get(k) or d)

    total_assets       = g("total_assets",       g("totale_attivo"))
    equity             = g("equity",             g("patrimonio_netto"))
    current_assets     = g("current_assets",     g("attivo_corrente"))
    current_liabilities= g("current_liabilities",g("passivo_corrente"))
    revenue            = g("revenue",            g("ricavi_netti", g("fatturato")))
    ebitda             = g("ebitda")
    ebit               = g("ebit")
    net_income         = g("net_income",         g("utile_netto"))
    interest_expense   = g("interest_expense",   g("oneri_finanziari"))
    total_debt         = g("total_debt",         g("debiti_finanziari", g("totale_debiti")))
    depreciation       = g("depreciation",       g("ammortamenti"))
    working_capital    = g("working_capital",    current_assets - current_liabilities)
    operating_cf       = g("operating_cashflow", ebitda * 0.8)  # stima se non disponibile
    debt_service       = g("debt_service",       interest_expense + total_debt * 0.10)  # stima

    # Calcola EBITDA se mancante
    if ebitda == 0.0 and ebit != 0.0:
        ebitda = ebit + depreciation

    results = {}

    # ── 1. DSCR (Debt Service Coverage Ratio) ─────────────────────────────
    # Soglia legale: DSCR >= 1.0
    if debt_service > 0:
        dscr = operating_cf / debt_service
    else:
        dscr = 999.0  # nessun debito = nessun rischio
    results["dscr"] = {
        "nome": "DSCR (Debt Service Coverage Ratio)",
        "formula": "Cash Flow Operativo / Servizio del Debito",
        "valore": round(dscr, 3),
        "soglia": ">= 1.0",
        "stato": "ok" if dscr >= 1.0 else ("warning" if dscr >= 0.8 else "danger"),
        "note": (
            "DSCR adeguato: l'azienda genera cassa sufficiente a servire il debito."
            if dscr >= 1.0 else
            f"ALERT: DSCR {dscr:.2f} < 1.0 — potenziale incapacita' a rimborsare il debito (art. 13 CCII)"
        ),
        "riferimento": "Art. 13 D.Lgs. 14/2019; D.L. 118/2021"
    }

    # ── 2. Oneri Finanziari / Ricavi ──────────────────────────────────────
    # Soglia settoriale CNDCEC (luglio 2019)
    soglia_of = SOGLIE_OF_RICAVI.get(settore.lower(), 0.06)
    of_ricavi = (interest_expense / revenue) if revenue > 0 else 0.0
    results["of_ricavi"] = {
        "nome": "Sostenibilita' Oneri Finanziari (OF/Ricavi)",
        "formula": "Oneri Finanziari / Ricavi netti",
        "valore": round(of_ricavi, 4),
        "valore_pct": f"{of_ricavi * 100:.2f}%",
        "soglia": f"<= {soglia_of * 100:.0f}% (settore: {settore})",
        "stato": "ok" if of_ricavi <= soglia_of else ("warning" if of_ricavi <= soglia_of * 1.5 else "danger"),
        "note": (
            "Oneri finanziari sostenibili rispetto ai ricavi."
            if of_ricavi <= soglia_of else
            f"ALERT: OF/Ricavi {of_ricavi*100:.1f}% supera soglia CNDCEC {soglia_of*100:.0f}%"
        ),
        "riferimento": "CNDCEC - Indici di allerta, luglio 2019"
    }

    # ── 3. Adeguatezza Patrimoniale (PN/Totale Attivo) ───────────────────
    # Soglia: >= 8% (equity ratio minimo)
    eq_ratio = (equity / total_assets) if total_assets > 0 else 0.0
    pn_negativo = equity < 0
    results["adeguatezza_patrimoniale"] = {
        "nome": "Adeguatezza Patrimoniale (PN/Attivo)",
        "formula": "Patrimonio Netto / Totale Attivo",
        "valore": round(eq_ratio, 4),
        "valore_pct": f"{eq_ratio * 100:.2f}%",
        "soglia": ">= 8%",
        "stato": "danger" if pn_negativo else ("ok" if eq_ratio >= 0.08 else "warning"),
        "note": (
            "ALLERTA CRITICA: Patrimonio netto negativo — perdita superiore al capitale sociale (art. 2447 c.c.)"
            if pn_negativo else
            (f"Patrimonio adeguato ({eq_ratio*100:.1f}%)." if eq_ratio >= 0.08
             else f"ALERT: Equity ratio {eq_ratio*100:.1f}% sotto soglia minima 8%")
        ),
        "riferimento": "Art. 2447 c.c.; Art. 2482-ter c.c.; Art. 13 CCII"
    }

    # ── 4. Ritorno Liquido dell'Attivo (CF Operativo / Totale Attivo) ────
    # Soglia: >= 0% (deve essere positivo)
    rla = (operating_cf / total_assets) if total_assets > 0 else 0.0
    results["ritorno_liquido_attivo"] = {
        "nome": "Ritorno Liquido dell'Attivo",
        "formula": "Cash Flow Operativo / Totale Attivo",
        "valore": round(rla, 4),
        "valore_pct": f"{rla * 100:.2f}%",
        "soglia": ">= 0%",
        "stato": "ok" if rla >= 0 else ("warning" if rla >= -0.05 else "danger"),
        "note": (
            f"Attivo genera liquidita' operativa ({rla*100:.1f}%)."
            if rla >= 0 else
            f"ALERT: Ritorno liquido negativo {rla*100:.1f}% — l'attivo non genera cassa sufficiente"
        ),
        "riferimento": "CNDCEC - Indici di allerta, luglio 2019"
    }

    # ── 5. Liquidita' (Current Ratio) ─────────────────────────────────────
    # Soglia: >= 1.0
    if current_liabilities > 0:
        current_ratio = current_assets / current_liabilities
    else:
        current_ratio = 999.0
    results["liquidita"] = {
        "nome": "Indice di Liquidita' (Current Ratio)",
        "formula": "Attivo Corrente / Passivo Corrente",
        "valore": round(current_ratio, 3),
        "soglia": ">= 1.0",
        "stato": "ok" if current_ratio >= 1.0 else ("warning" if current_ratio >= 0.8 else "danger"),
        "note": (
            f"Liquidita' adeguata (ratio: {current_ratio:.2f})."
            if current_ratio >= 1.0 else
            f"ALERT: Illiquidita' a breve termine — passivo corrente supera attivo corrente (ratio: {current_ratio:.2f})"
        ),
        "riferimento": "Art. 13 CCII; OIC 12"
    }

    # ── 6. PFN / EBITDA (Leverage) ────────────────────────────────────────
    # Soglia: <= 6x (critico), <= 4x (attenzione)
    if ebitda > 0:
        pfn_ebitda = total_debt / ebitda
    elif ebitda < 0:
        pfn_ebitda = 999.0  # EBITDA negativo = situazione critica
    else:
        pfn_ebitda = 0.0
    results["pfn_ebitda"] = {
        "nome": "Leva Finanziaria (PFN/EBITDA)",
        "formula": "Posizione Finanziaria Netta / EBITDA",
        "valore": round(pfn_ebitda, 2),
        "soglia": "<= 4x (attenzione); <= 6x (limite critico)",
        "stato": "ok" if pfn_ebitda <= 4 else ("warning" if pfn_ebitda <= 6 else "danger"),
        "note": (
            f"Leverage sostenibile (PFN/EBITDA: {pfn_ebitda:.1f}x)."
            if pfn_ebitda <= 4 else
            (f"ATTENZIONE: leverage elevato {pfn_ebitda:.1f}x (soglia bancaria 4x)" if pfn_ebitda <= 6
             else f"ALLERTA CRITICA: leverage {pfn_ebitda:.1f}x — insostenibile, rischio insolvenza")
        ),
        "riferimento": "Prassi bancaria CRD IV; Linee guida BCE crediti deteriorati"
    }

    # ── 7. Coverage Oneri Finanziari (EBITDA / OF) ───────────────────────
    # Soglia: >= 2x (minimo accettabile)
    if interest_expense > 0:
        interest_coverage = ebitda / interest_expense
    else:
        interest_coverage = 999.0
    results["interest_coverage"] = {
        "nome": "Coverage Oneri Finanziari (EBITDA/OF)",
        "formula": "EBITDA / Oneri Finanziari",
        "valore": round(interest_coverage, 2),
        "soglia": ">= 2x",
        "stato": "ok" if interest_coverage >= 2 else ("warning" if interest_coverage >= 1 else "danger"),
        "note": (
            f"Coverage adeguato ({interest_coverage:.1f}x)."
            if interest_coverage >= 2 else
            (f"ATTENZIONE: coverage basso {interest_coverage:.1f}x" if interest_coverage >= 1
             else f"ALLERTA: EBITDA non copre gli oneri finanziari (coverage: {interest_coverage:.1f}x)")
        ),
        "riferimento": "Prassi bancaria italiana; EBA Guidelines on Loan Origination"
    }

    # ── Conteggio alert ───────────────────────────────────────────────────
    danger_count  = sum(1 for v in results.values() if v["stato"] == "danger")
    warning_count = sum(1 for v in results.values() if v["stato"] == "warning")
    ok_count      = sum(1 for v in results.values() if v["stato"] == "ok")

    # Giudizio complessivo
    if danger_count >= 3 or pn_negativo:
        giudizio = "CRISI CONCLAMATA"
        giudizio_desc = (
            "Situazione di crisi d'impresa conclamata. Obbligo di attivare "
            "immediatamente la procedura di Composizione Negoziata ex D.L. 118/2021 "
            "o altra procedura concorsuale. L'organo amministrativo e' tenuto ad "
            "adottare misure idonee ai sensi dell'art. 2086 c.c."
        )
        giudizio_stato = "danger"
    elif danger_count >= 1 or warning_count >= 3:
        giudizio = "SEGNALI DI ALLERTA"
        giudizio_desc = (
            "Rilevati segnali di allerta ex art. 13 CCII. L'organo di controllo "
            "e' tenuto a segnalare tempestivamente all'organo amministrativo. "
            "Valutare l'attivazione volontaria della Composizione Negoziata o "
            "piani di risanamento ex art. 56 CCII."
        )
        giudizio_stato = "warning"
    else:
        giudizio = "EQUILIBRIO FINANZIARIO"
        giudizio_desc = (
            "Gli indici di allerta non evidenziano segnali di crisi ai sensi del CCII. "
            "Si raccomanda il monitoraggio trimestrale degli indicatori e il mantenimento "
            "di adeguati assetti organizzativi, amministrativi e contabili ex art. 2086 c.c."
        )
        giudizio_stato = "ok"

    results["_meta"] = {
        "giudizio": giudizio,
        "giudizio_desc": giudizio_desc,
        "giudizio_stato": giudizio_stato,
        "danger_count": danger_count,
        "warning_count": warning_count,
        "ok_count": ok_count,
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
    """
    Genera il PDF "Relazione sugli Indici di Allerta" conforme D.Lgs. 14/2019.
    Restituisce bytes pronti per download o allegato.
    """
    indici = calcola_indici_ccii(data, settore)
    meta   = indici.pop("_meta")

    pdf = NexusPDF(company_name=company_name, report_type="Crisi d'Impresa CCII")
    pdf.add_page()

    # ── INTESTAZIONE LEGALE ────────────────────────────────────────────────
    # Banner rosso/giallo in base al giudizio
    banner_colors = {"danger": (183, 28, 28), "warning": (245, 127, 23), "ok": (46, 125, 50)}
    bc = banner_colors[meta["giudizio_stato"]]
    pdf.set_fill_color(*bc)
    pdf.rect(0, 18, 210, 60, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_xy(10, 20)
    pdf.cell(190, 5, "RELAZIONE SUGLI INDICI DI ALLERTA DELLA CRISI D'IMPRESA", align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(10, 26)
    pdf.cell(190, 5, "D.Lgs. 14/2019 (CCII) - D.Lgs. 83/2022 - D.L. 118/2021 - CNDCEC 2019", align="C")
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(10, 34)
    pdf.cell(190, 12, clean_text(company_name.upper()), align="C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(10, 50)
    pdf.cell(190, 10, clean_text(meta["giudizio"]), align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_xy(10, 62)
    pdf.cell(190, 5, clean_text(f"Analisi del {meta['data_analisi']} | Settore: {settore.title()} | Elaborata da: {user_name}"), align="C")
    pdf.ln(52)

    # ── RIEPILOGO ALERT ────────────────────────────────────────────────────
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "B", 11)
    colw = 60
    # tre box affiancati
    boxes = [
        (meta["danger_count"],  "ALLERTE CRITICHE",  (183, 28, 28)),
        (meta["warning_count"], "SEGNALI ATTENZIONE",(245, 127, 23)),
        (meta["ok_count"],      "INDICI OK",         (46, 125, 50)),
    ]
    pdf.set_xy(10, pdf.get_y() + 2)
    for val, label, color in boxes:
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 22)
        pdf.cell(colw, 14, str(val), fill=True, align="C")
        pdf.set_x(pdf.get_x())
    pdf.ln(14)
    pdf.set_x(10)
    for val, label, color in boxes:
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(colw, 6, clean_text(label), fill=True, align="C")
    pdf.ln(8)

    # ── GIUDIZIO COMPLESSIVO ───────────────────────────────────────────────
    pdf.section_title("GIUDIZIO COMPLESSIVO AI SENSI DEL CCII")
    gc = banner_colors[meta["giudizio_stato"]]
    pdf.set_fill_color(*gc)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(0, 7, clean_text(f"  {meta['giudizio_desc']}"), fill=True)
    pdf.ln(3)

    # ── INDICI DI ALLERTA CCII ─────────────────────────────────────────────
    pdf.section_title("INDICI DI ALLERTA - ANALISI DETTAGLIATA (CNDCEC 2019)")

    stato_labels = {"ok": "OK", "warning": "ATTENZIONE", "danger": "ALLERTA"}
    stato_colors = {"ok": SUCCESS, "warning": WARNING, "danger": DANGER}

    for key, indice in indici.items():
        if key.startswith("_"):
            continue
        sc = stato_colors[indice["stato"]]
        pdf.set_fill_color(*sc)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 7, clean_text(f"  [{stato_labels[indice['stato']]}]  {indice['nome']}"),
                 fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Tabella indice
        rows = [
            ("Formula di calcolo",   indice["formula"]),
            ("Valore calcolato",      indice.get("valore_pct", str(indice["valore"]))),
            ("Soglia normativa",      indice["soglia"]),
            ("Riferimento normativo", indice["riferimento"]),
        ]
        pdf.set_text_color(*DARK_TEXT)
        fill = False
        pdf.set_font("Helvetica", "", 8)
        for label, val in rows:
            pdf.set_fill_color(240, 248, 255) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(80, 5, clean_text(label), fill=True, border=1)
            pdf.cell(110, 5, clean_text(str(val)), fill=True, border=1,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            fill = not fill

        # Nota sintetica
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_fill_color(*sc)
        pdf.set_text_color(255, 255, 255)
        pdf.multi_cell(0, 5, clean_text(f"  => {indice['note']}"), fill=True)
        pdf.ln(3)

    # ── OBBLIGHI LEGALI ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("OBBLIGHI LEGALI E ADEMPIMENTI")
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "", 9)

    obblighi = [
        ("Art. 2086 c.c.",
         "L'organo amministrativo deve istituire assetti organizzativi, amministrativi e "
         "contabili adeguati alla natura e dimensioni dell'impresa, con funzione di rilevazione "
         "tempestiva della crisi."),
        ("Art. 25-octies CCII (ex art. 13)",
         "Gli indici di allerta pubblicati dal CNDCEC costituiscono presupposto per "
         "l'emersione anticipata della crisi. Il superamento delle soglie impone "
         "segnalazione all'organo di controllo entro 30 giorni."),
        ("D.L. 118/2021 - Composizione Negoziata",
         "L'imprenditore in condizioni di squilibrio patrimoniale o economico-finanziario "
         "che rendano probabile la crisi o l'insolvenza puo' richiedere la nomina di un "
         "esperto indipendente alla Camera di Commercio."),
        ("Art. 56 CCII - Piano Attestato di Risanamento",
         "Piano di risanamento idoneo a consentire il risanamento dell'esposizione "
         "debitoria e il riequilibrio della situazione finanziaria, attestato da un "
         "professionista indipendente."),
        ("Art. 84 CCII - Concordato Preventivo",
         "Procedura concorsuale che permette all'imprenditore in stato di crisi o "
         "insolvenza di proporre ai creditori un piano di soddisfazione dei loro crediti."),
    ]
    for norma, testo in obblighi:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*PRIMARY)
        pdf.cell(0, 6, clean_text(norma), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*DARK_TEXT)
        pdf.multi_cell(0, 5, clean_text(testo))
        pdf.ln(2)

    # ── TIMELINE RACCOMANDAZIONI ───────────────────────────────────────────
    pdf.section_title("PIANO D'AZIONE CONSIGLIATO")
    pdf.set_text_color(*DARK_TEXT)

    if meta["giudizio_stato"] == "danger":
        azioni = [
            ("IMMEDIATO (0-30 giorni)",   "danger",
             "Convocare CdA straordinario. Redigere piano di risanamento urgente. "
             "Valutare Composizione Negoziata ex D.L. 118/2021. Informare i soci delle perdite."),
            ("BREVE TERMINE (1-3 mesi)",  "danger",
             "Nominare advisor finanziario. Avviare trattative con istituti di credito "
             "per ristrutturazione del debito. Identificare asset non strategici da dismettere."),
            ("MEDIO TERMINE (3-12 mesi)", "warning",
             "Implementare piano industriale di rilancio. Monitorare KPI mensili. "
             "Verificare compliance CCII con revisore legale."),
        ]
    elif meta["giudizio_stato"] == "warning":
        azioni = [
            ("BREVE TERMINE (0-60 giorni)", "warning",
             "Analizzare cause del deterioramento. Predisporre piano di miglioramento. "
             "Rafforzare flusso di cassa operativo."),
            ("MEDIO TERMINE (2-6 mesi)", "warning",
             "Rinegoziare condizioni bancarie. Ottimizzare capitale circolante. "
             "Valutare operazioni straordinarie (aumento capitale, cessione rami d'azienda)."),
            ("LUNGO TERMINE (6-18 mesi)", "ok",
             "Raggiungere equilibrio finanziario sostenibile. Monitoraggio continuo "
             "con NEXUS Finance Pro."),
        ]
    else:
        azioni = [
            ("MONITORAGGIO CONTINUO", "ok",
             "Mantenere monitoraggio trimestrale degli indici CCII con NEXUS Finance Pro. "
             "Aggiornare l'analisi ad ogni chiusura di periodo."),
            ("OTTIMIZZAZIONE", "ok",
             "Esplorare opportunita' di crescita. Valutare investimenti e fabbisogno "
             "finanziario in ottica bancaria."),
        ]

    for timing, stato, testo in azioni:
        sc = stato_colors[stato]
        pdf.set_fill_color(*sc)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, clean_text(f"  {timing}"), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 5, clean_text(f"  {testo}"), fill=True)
        pdf.ln(2)

    # ── DISCLAIMER LEGALE ─────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_draw_color(*GRAY)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*GRAY)
    disclaimer = (
        "AVVERTENZA LEGALE: Il presente documento e' elaborato da NEXUS Finance Pro su dati "
        "forniti dall'utente e ha finalita' informative e di supporto decisionale. Non costituisce "
        "parere legale, consulenza professionale ai sensi del D.Lgs. 139/2005, ne' attestazione "
        "professionale ai sensi dell'art. 56 CCII. Per la predisposizione di piani di risanamento "
        "attestati, concordati preventivi o domande di Composizione Negoziata, e' necessario "
        "rivolgersi a professionisti abilitati (Dottori Commercialisti, Avvocati). "
        "Il report puo' essere allegato a pratiche bancarie, relazioni al CdA e all'organo di "
        "controllo come documento di supporto all'analisi finanziaria aziendale."
    )
    pdf.multi_cell(0, 4, clean_text(disclaimer))

    if revisore:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*DARK_TEXT)
        pdf.cell(90, 6, "Elaborato da:", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 6, "Firma e timbro:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 6, clean_text(revisore), new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(90, 6, "_" * 30, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())
