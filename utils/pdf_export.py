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


class NexusPDF(FPDF):

    def __init__(self, company_name: str = "", report_type: str = ""):
        super().__init__()
        self.company_name = company_name
        self.report_type = report_type
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Barra header
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
        self.cell(130, 6, "NEXUS Finance Pro — Report riservato e confidenziale")
        self.cell(60, 6, f"Pagina {self.page_no()}", align="R")

    def section_title(self, title: str, icon: str = ""):
        self.ln(4)
        self.set_fill_color(*ACCENT)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {icon}  {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def kpi_box(self, label: str, value: str, color=None):
        if color is None:
            color = PRIMARY
        self.set_fill_color(*color)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.cell(44, 6, label, fill=True, align="C")
        self.set_fill_color(240, 248, 255)
        self.set_text_color(*DARK_TEXT)
        self.set_font("Helvetica", "B", 10)
        self.cell(44, 8, value, fill=True, align="C", border=1)

    def two_col_table(self, rows: List[tuple], col1: str = "Indicatore", col2: str = "Valore"):
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.cell(110, 7, col1, fill=True, border=1)
        self.cell(60, 7, col2, fill=True, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        fill = False
        for i, (k, v) in enumerate(rows):
            self.set_fill_color(240, 248, 255) if fill else self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_TEXT)
            self.set_font("Helvetica", "", 9)
            self.cell(110, 6, str(k), fill=True, border=1)
            self.set_font("Helvetica", "B", 9)
            self.cell(60, 6, str(v), fill=True, border=1, align="R",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            fill = not fill
        self.ln(3)

    def three_col_table(self, headers: List[str], rows: List[tuple]):
        widths = [70, 50, 50]
        self.set_fill_color(*PRIMARY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, fill=True, border=1)
        self.ln()
        fill = False
        for row in rows:
            self.set_fill_color(240, 248, 255) if fill else self.set_fill_color(*WHITE)
            self.set_text_color(*DARK_TEXT)
            self.set_font("Helvetica", "", 9)
            for val, w in zip(row, widths):
                self.cell(w, 6, str(val), fill=True, border=1)
            self.ln()
            fill = not fill
        self.ln(3)

    def alert_box(self, text: str, kind: str = "warning"):
        colors = {"warning": WARNING, "danger": DANGER, "ok": SUCCESS, "info": ACCENT}
        c = colors.get(kind, WARNING)
        self.set_fill_color(c[0], c[1], c[2])
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        self.multi_cell(0, 6, f"  {text}", fill=True)
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
    pdf.cell(180, 10, company_name.upper(), align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 56)
    pdf.cell(180, 8,
             f"Generato il {datetime.datetime.now().strftime('%d %B %Y')} da {user_name}",
             align="C")
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
        pdf.cell(85, 18, f"{score:.0f}/100 — {ratio_result.health_label}", fill=True, align="C")
        pdf.ln(18)

    # ── RIEPILOGO ESECUTIVO ────────────────────────────────────────────────
    pdf.section_title("RIEPILOGO ESECUTIVO", "📋")

    if raw_data:
        fmt = lambda v: f"€ {v:,.0f}" if isinstance(v, (int, float)) else str(v)
        kpis = [
            ("Totale Attivo", fmt(raw_data.get("total_assets", 0))),
            ("Ricavi", fmt(raw_data.get("revenue", 0))),
            ("EBITDA", fmt(raw_data.get("ebitda", 0))),
            ("Patrimonio Netto", fmt(raw_data.get("equity", 0))),
            ("Utile Netto", fmt(raw_data.get("net_income", 0))),
            ("Totale Passivo", fmt(raw_data.get("total_liabilities", 0))),
        ]
        pdf.two_col_table(kpis, "Voce di Bilancio", "Valore (€)")

    # ── ALTMAN Z-SCORE ─────────────────────────────────────────────────────
    if altman_result:
        pdf.section_title("ALTMAN Z-SCORE — PROBABILITÀ DI FALLIMENTO", "🎯")
        pdf.set_font("Helvetica", "B", 13)
        zone_colors = {"safe": SUCCESS, "grey": WARNING, "distress": DANGER}
        zc = zone_colors.get(altman_result.zone, GRAY)
        pdf.set_fill_color(*zc)
        pdf.set_text_color(*WHITE)
        pdf.cell(0, 10,
                 f"  Z-Score: {altman_result.z_score}   |   {altman_result.zone_label}   |   "
                 f"Prob. Fallimento: {altman_result.bankruptcy_probability:.1f}%",
                 fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        pdf.set_text_color(*DARK_TEXT)
        var_rows = [(k, f"{v:.4f}") for k, v in altman_result.variables.items()]
        pdf.two_col_table(var_rows, "Variabile Z-Score", "Valore")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GRAY)
        pdf.multi_cell(0, 5, f"Modello: {altman_result.model} | Rating: {altman_result.rating}")
        pdf.set_text_color(*DARK_TEXT)
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, f"Raccomandazione: {altman_result.recommendation}")
        pdf.ln(3)

    # ── RATIO ANALYSIS ─────────────────────────────────────────────────────
    if ratio_result:
        pdf.section_title("ANALISI RATIOS FINANZIARI", "📊")
        for cat in ratio_result.categories:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*PRIMARY)
            score_c = SUCCESS if cat.score >= 70 else (WARNING if cat.score >= 40 else DANGER)
            pdf.set_fill_color(*score_c)
            pdf.set_text_color(*WHITE)
            pdf.cell(0, 7, f"  {cat.icon} {cat.name}   [Score: {cat.score:.0f}/100]",
                     fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            rows = [(r.name, r.formatted) for r in cat.ratios if r.value != 0]
            if rows:
                pdf.two_col_table(rows, "Ratio", "Valore")

        # Alert e punti di forza
        if ratio_result.key_alerts:
            pdf.section_title("ALERT PRINCIPALI", "⚠️")
            for alert in ratio_result.key_alerts:
                pdf.alert_box(alert, "warning")
        if ratio_result.strengths:
            pdf.section_title("PUNTI DI FORZA", "✅")
            for s in ratio_result.strengths:
                pdf.alert_box(s, "ok")

    # ── CASH FLOW ──────────────────────────────────────────────────────────
    if cashflow_result:
        pdf.section_title("RENDICONTO FINANZIARIO (METODO INDIRETTO)", "💰")
        cf_rows = [
            ("Utile Netto", f"€ {cashflow_result.net_income:,.0f}"),
            ("(+) Ammortamenti", f"€ {cashflow_result.depreciation:,.0f}"),
            ("(±) Δ Capitale Circolante", f"€ {cashflow_result.delta_working_capital:,.0f}"),
            ("= CASH FLOW OPERATIVO", f"€ {cashflow_result.operating_cashflow:,.0f}"),
            ("(−) CapEx", f"€ {-cashflow_result.capex:,.0f}"),
            ("= FREE CASH FLOW", f"€ {cashflow_result.free_cashflow:,.0f}"),
            ("Cash Flow Finanziario", f"€ {cashflow_result.financing_cashflow:,.0f}"),
            ("VARIAZIONE NETTA CASSA", f"€ {cashflow_result.net_change:,.0f}"),
        ]
        pdf.two_col_table(cf_rows, "Voce", "Importo")

        if cashflow_result.covenants:
            pdf.section_title("COVENANT BANCARI", "🏦")
            cov_rows = [(c["Covenant"], c["Valore"], c["Status"])
                        for c in cashflow_result.covenants]
            pdf.three_col_table(["Covenant", "Valore", "Status"], cov_rows)

        if cashflow_result.alerts:
            for a in cashflow_result.alerts:
                kind = "danger" if "🔴" in a else "warning"
                pdf.alert_box(a, kind)

    # ── FOOTER PAGE ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("NOTE METODOLOGICHE", "📝")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK_TEXT)
    notes = [
        "• Altman Z-Score: modelli 1968 (quotate), 1983 (private), 1995 (non manifatturiere)",
        "• Financial Ratios: calcolati secondo standard IFRS e prassi bancaria italiana",
        "• Cash Flow: metodo indiretto, proiezioni a 5 anni (scenario base e stress)",
        "• Benchmark: medie di settore italiane aggiornate (fonte: Banca d'Italia, CEBI)",
        "• Il presente report ha finalità informative e non costituisce consulenza finanziaria",
        "• I dati sono quelli inseriti dall'utente — verificare sempre la fonte dei bilanci",
    ]
    for note in notes:
        pdf.multi_cell(0, 6, note)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(0, 8, "NEXUS Finance Pro — La tua piattaforma di analisi finanziaria",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    return bytes(pdf.output())
