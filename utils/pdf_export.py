"""
NEXUS Finance Pro — PDF Report Generator
Report professionale con header, sezioni, tabelle e footer.
Usa fpdf2 (puro Python, nessuna dipendenza da wkhtmltopdf).
"""
from fpdf import FPDF, XPos, YPos
from fpdf.enums import TableCellFillMode
import datetime
import io
from typing import Dict, List, Optional, Any


PRIMARY = (13, 71, 161)      # Blu NEXUS
ACCENT = (0, 150, 136)       # Verde teal
DANGER = (183, 28, 28)       # Rosso
WARNING = (245, 127, 23)     # Arancione
SUCCESS = (46, 125, 50)      # Verde
LIGHT_BG = (240, 248, 255)   # Sfondo chiaro
DARK_TEXT = (20, 20, 40)
GRAY = (100, 100, 120)
WHITE = (255, 255, 255)


def clean_text(text: str) -> str:
    """
    Sostituisce caratteri Unicode non supportati da Helvetica (Latin-1/cp1252)
    con equivalenti ASCII sicuri. Previene CharacterNotFoundError in fpdf2.
    """
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        # Trattini tipografici
        "\u2014": " - ",   # em dash —
        "\u2013": " - ",   # en dash -
        "\u2012": "-",     # figure dash
        "\u2015": "-",     # horizontal bar
        # Virgolette tipografiche
        "\u201C": '"',     # left double quotation \u201c
        "\u201D": '"',     # right double quotation \u201d
        "\u2018": "'",     # left single quotation
        "\u2019": "'",     # right single quotation
        "\u201A": "'",     # single low quotation
        "\u201E": '"',     # double low quotation
        # Punteggiatura varia
        "\u2026": "...",   # ellipsis
        "\u2022": "*",     # bullet
        "\u2023": "-",     # triangular bullet
        "\u25CF": "*",     # black circle
        "\u25BA": ">",     # black right-pointing pointer
        # Frecce
        "\u2192": "->",    # rightwards arrow
        "\u2190": "<-",    # leftwards arrow
        "\u2191": "^",     # upwards arrow
        "\u2193": "v",     # downwards arrow
        "\u21D2": "=>",    # rightwards double arrow
        # Simboli matematici
        "\u00D7": "x",     # multiplication sign
        "\u00F7": "/",     # division sign
        "\u2212": "-",     # minus sign
        "\u00B1": "+/-",   # plus-minus
        "\u2264": "<=",    # less-than or equal
        "\u2265": ">=",    # greater-than or equal
        # Simboli speciali
        "\u00A9": "(c)",   # copyright
        "\u00AE": "(R)",   # registered
        "\u2122": "(TM)",  # trademark
        "\u00B0": "deg",   # degree
        # Emoji / simboli grafici comuni nei report
        "\U0001F4CA": "[Chart]",
        "\U0001F3AF": "[Target]",
        "\U0001F4B0": "[Money]",
        "\U0001F4C8": "[Up]",
        "\U0001F4C9": "[Down]",
        "\u26A0": "[!]",   # warning sign
        "\u2705": "[OK]",  # check mark
        "\u274C": "[X]",   # cross mark
        "\u2714": "OK",    # heavy check mark
        "\u2716": "X",     # heavy multiplication
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Rimuovi qualsiasi altro carattere fuori da Latin-1 (codepage 1252)
    result = ""
    for ch in text:
        try:
            ch.encode("cp1252")
            result += ch
        except (UnicodeEncodeError, UnicodeDecodeError):
            result += "?"
    return result


class NexusPDF(FPDF):

    def __init__(self, company_name: str = "", report_type: str = ""):
        super().__init__()
        self.company_name = clean_text(company_name)
        self.report_type = clean_text(report_type)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_fill_color(*PRIMARY)
        self.rect(0, 0, 210, 18, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 12)
        self.set_xy(8, 4)
        self.cell(80, 8, "NEXUS Finance Pro", align="L")
        self.set_font("Helvetica", "", 9)
        self.set_xy(90, 4)
        self.cell(80, 8, self.company_name, align="C")
        self.set_xy(140, 4)
        self.cell(60, 8, datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-14)
        self.set_fill_color(*PRIMARY)
        self.rect(0, self.get_y(), 210, 14, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "I", 8)
        self.set_xy(8, self.get_y() + 3)
        self.cell(130, 6, "NEXUS Finance Pro - Report riservato e confidenziale")
        self.cell(60, 6, f"Pagina {self.page_no()}", align="R")

    def section_title(self, title: str, icon: str = ""):
        self.ln(4)
        self.set_fill_color(*ACCENT)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        label = clean_text(f"  {title}")
        self.cell(0, 8, label, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def kpi_box(self, label: str, value: str, color=None):
        if color is None:
            color = PRIMARY
        self.set_fill_color(*color)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.cell(44, 6, clean_text(label), fill=True, align="C")
        self.set_fill_color(240, 248, 255)
        self.set_text_color(*DARK_TEXT)
        self.set_font("Helvetica", "B", 10)
        self.cell(44, 8, clean_text(value), fill=True, align="C", border=1)

    def two_col_table(self, rows: List[tuple], col1: str = "Indicatore", col2: str = "Valore"):
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.cell(110, 7, clean_text(col1), fill=True, border=1)
        self.cell(60, 7, clean_text(col2), fill=True, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        fill = False
        for i, (k, v) in enumerate(rows):
            self.set_fill_color(240, 248, 255) if fill else self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_TEXT)
            self.set_font("Helvetica", "", 9)
            self.cell(110, 6, clean_text(str(k)), fill=True, border=1)
            self.set_font("Helvetica", "B", 9)
            self.cell(60, 6, clean_text(str(v)), fill=True, border=1, align="R",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            fill = not fill
        self.ln(3)

    def three_col_table(self, headers: List[str], rows: List[tuple]):
        widths = [70, 50, 50]
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for h, w in zip(headers, widths):
            self.cell(w, 7, clean_text(h), fill=True, border=1)
        self.ln()
        fill = False
        for row in rows:
            self.set_fill_color(240, 248, 255) if fill else self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_TEXT)
            self.set_font("Helvetica", "", 9)
            for val, w in zip(row, widths):
                self.cell(w, 6, clean_text(str(val)), fill=True, border=1)
            self.ln()
            fill = not fill
        self.ln(3)

    def alert_box(self, text: str, kind: str = "warning"):
        colors = {"warning": WARNING, "danger": DANGER, "ok": SUCCESS, "info": ACCENT}
        c = colors.get(kind, WARNING)
        self.set_fill_color(c[0], c[1], c[2])
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.multi_cell(0, 6, clean_text(f"  {text}"), fill=True)
        self.ln(1)


def generate_full_report(
    company_name: str,
    altman_result: Optional[Any] = None,
    ratio_result: Optional[Any] = None,
    cashflow_result: Optional[Any] = None,
    credit_result: Optional[Any] = None,
    raw_data: Optional[Dict] = None,
    user_name: str = "NEXUS Finance Pro",
) -> bytes:
    """
    Genera report PDF completo. Restituisce bytes pronti per download.
    """
    pdf = NexusPDF(company_name=company_name, report_type="Analisi Finanziaria Completa")
    pdf.add_page()

    # ── COPERTINA ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*PRIMARY)
    pdf.rect(0, 18, 210, 55, "F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_xy(15, 24)
    pdf.cell(180, 12, "ANALISI FINANZIARIA COMPLETA", align="C")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(15, 40)
    pdf.cell(180, 10, clean_text(company_name.upper()), align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 56)
    pdf.cell(
        180, 8,
        clean_text(f"Generato il {datetime.datetime.now().strftime('%d %B %Y')} da {user_name}"),
        align="C"
    )
    pdf.ln(40)

    # Score complessivo
    if ratio_result:
        score = ratio_result.overall_score
        score_color = SUCCESS if score >= 75 else (WARNING if score >= 40 else DANGER)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*DARK_TEXT)
        pdf.set_xy(15, 82)
        pdf.cell(90, 10, "HEALTH SCORE FINANZIARIO", align="C")
        pdf.set_fill_color(*score_color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_xy(110, 78)
        pdf.cell(
            85, 18,
            clean_text(f"{score:.0f}/100 - {ratio_result.health_label}"),
            fill=True, align="C"
        )
        pdf.ln(18)

    # ── RIEPILOGO ESECUTIVO ────────────────────────────────────────────────
    pdf.section_title("RIEPILOGO ESECUTIVO")

    if raw_data:
        fmt = lambda v: f"EUR {v:,.0f}" if isinstance(v, (int, float)) else str(v)
        kpis = [
            ("Totale Attivo", fmt(raw_data.get("total_assets", 0))),
            ("Ricavi", fmt(raw_data.get("revenue", 0))),
            ("EBITDA", fmt(raw_data.get("ebitda", 0))),
            ("Patrimonio Netto", fmt(raw_data.get("equity", 0))),
            ("Utile Netto", fmt(raw_data.get("net_income", 0))),
            ("Totale Passivo", fmt(raw_data.get("total_liabilities", 0))),
        ]
        pdf.two_col_table(kpis, "Voce di Bilancio", "Valore (EUR)")

    # ── ALTMAN Z-SCORE ─────────────────────────────────────────────────────
    if altman_result:
        pdf.section_title("ALTMAN Z-SCORE - PROBABILITA' DI FALLIMENTO")
        pdf.set_font("Helvetica", "B", 13)
        zone_colors = {"safe": SUCCESS, "grey": WARNING, "distress": DANGER}
        zc = zone_colors.get(altman_result.zone, GRAY)
        pdf.set_fill_color(*zc)
        pdf.set_text_color(*WHITE)
        label = clean_text(
            f"  Z-Score: {altman_result.z_score}   |   {altman_result.zone_label}   |   "
            f"Prob. Fallimento: {altman_result.bankruptcy_probability:.1f}%"
        )
        pdf.cell(0, 10, label, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        pdf.set_text_color(*DARK_TEXT)
        var_rows = [(k, f"{v:.4f}") for k, v in altman_result.variables.items()]
        pdf.two_col_table(var_rows, "Variabile Z-Score", "Valore")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GRAY)
        pdf.multi_cell(0, 5, clean_text(f"Modello: {altman_result.model} | Rating: {altman_result.rating}"))
        pdf.set_text_color(*DARK_TEXT)
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, clean_text(f"Raccomandazione: {altman_result.recommendation}"))
        pdf.ln(3)

    # ── RATIO ANALYSIS ─────────────────────────────────────────────────────
    if ratio_result:
        pdf.section_title("ANALISI RATIOS FINANZIARI")
        for cat in ratio_result.categories:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*PRIMARY)
            score_c = SUCCESS if cat.score >= 70 else (WARNING if cat.score >= 40 else DANGER)
            pdf.set_fill_color(*score_c)
            pdf.set_text_color(*WHITE)
            pdf.cell(
                0, 7,
                clean_text(f"  {cat.name}   [Score: {cat.score:.0f}/100]"),
                fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )
            rows = [(r.name, r.formatted) for r in cat.ratios if r.value != 0]
            if rows:
                pdf.two_col_table(rows, "Ratio", "Valore")

        if ratio_result.key_alerts:
            pdf.section_title("ALERT PRINCIPALI")
            for alert in ratio_result.key_alerts:
                pdf.alert_box(alert, "warning")
        if ratio_result.strengths:
            pdf.section_title("PUNTI DI FORZA")
            for s in ratio_result.strengths:
                pdf.alert_box(s, "ok")

    # ── CASH FLOW ──────────────────────────────────────────────────────────
    if cashflow_result:
        pdf.section_title("RENDICONTO FINANZIARIO (METODO INDIRETTO)")
        cf_rows = [
            ("Utile Netto", f"EUR {cashflow_result.net_income:,.0f}"),
            ("(+) Ammortamenti", f"EUR {cashflow_result.depreciation:,.0f}"),
            ("(+/-) Var. Capitale Circolante", f"EUR {cashflow_result.delta_working_capital:,.0f}"),
            ("= CASH FLOW OPERATIVO", f"EUR {cashflow_result.operating_cashflow:,.0f}"),
            ("(-) CapEx", f"EUR {-cashflow_result.capex:,.0f}"),
            ("= FREE CASH FLOW", f"EUR {cashflow_result.free_cashflow:,.0f}"),
            ("Cash Flow Finanziario", f"EUR {cashflow_result.financing_cashflow:,.0f}"),
            ("VARIAZIONE NETTA CASSA", f"EUR {cashflow_result.net_change:,.0f}"),
        ]
        pdf.two_col_table(cf_rows, "Voce", "Importo")

        if cashflow_result.covenants:
            pdf.section_title("COVENANT BANCARI")
            cov_rows = [(c["Covenant"], c["Valore"], c["Status"])
                        for c in cashflow_result.covenants]
            pdf.three_col_table(["Covenant", "Valore", "Status"], cov_rows)

        if cashflow_result.alerts:
            for a in cashflow_result.alerts:
                kind = "danger" if "rosso" in a.lower() or "critico" in a.lower() else "warning"
                pdf.alert_box(a, kind)

    # ── NOTE METODOLOGICHE ─────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("NOTE METODOLOGICHE")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK_TEXT)
    notes = [
        "* Altman Z-Score: modelli 1968 (quotate), 1983 (private), 1995 (non manifatturiere)",
        "* Financial Ratios: calcolati secondo standard IFRS e prassi bancaria italiana",
        "* Cash Flow: metodo indiretto, proiezioni a 5 anni (scenario base e stress)",
        "* Benchmark: medie di settore italiane aggiornate (fonte: Banca d'Italia, CEBI)",
        "* Il presente report ha finalita' informative e non costituisce consulenza finanziaria",
        "* I dati sono quelli inseriti dall'utente - verificare sempre la fonte dei bilanci",
    ]
    for note in notes:
        pdf.multi_cell(0, 6, note)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(
        0, 8,
        "NEXUS Finance Pro - La tua piattaforma di analisi finanziaria",
        align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )

    return bytes(pdf.output())
