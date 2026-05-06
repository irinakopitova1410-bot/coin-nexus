"""
NEXUS Finance Pro — Variance Analysis Suite
Analisi Scostamenti Budget vs Actual con Waterfall Chart
Conforme alle richieste Invitalia/Banche — D.Lgs. 14/2019 CCII

Features:
- Waterfall interattiva Budget -> Actual (Gross Margin -> EBITDA -> Risultato Netto)
- Breakdown per Business Unit (B&B, Casa, GMM, WHS, HB, CNR)
- 9 driver di scostamento quantificati
- Semaforo Covenant Bancari
- Export PDF per Invitalia/Banche
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
from datetime import datetime

# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt_eur(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"€{v/1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"€{v/1_000:.0f}K"
    return f"€{v:.0f}"

def fmt_pct(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"

def delta_color(v: float) -> str:
    if v > 0:
        return "#22c55e"
    elif v < 0:
        return "#ef4444"
    return "#64748b"

def delta_icon(v: float) -> str:
    if v > 0: return "▲"
    elif v < 0: return "▼"
    return "—"

# ─── Waterfall Chart ──────────────────────────────────────────────────────────

def waterfall_chart(labels, values, title="Waterfall Analisi Scostamenti"):
    """Grafico waterfall con valori cumulativi."""
    colors = []
    for i, (label, val) in enumerate(zip(labels, values)):
        if label in ("Budget", "Actual", "Piano", "Totale"):
            colors.append("#0D47A1")
        elif val >= 0:
            colors.append("#22c55e")
        else:
            colors.append("#ef4444")

    measure = []
    for label in labels:
        if label in ("Budget", "Piano"):
            measure.append("absolute")
        elif label in ("Actual", "Totale"):
            measure.append("total")
        else:
            measure.append("relative")

    fig = go.Figure(go.Waterfall(
        name="Scostamento",
        orientation="v",
        measure=measure,
        x=labels,
        y=values,
        text=[fmt_eur(v) for v in values],
        textposition="outside",
        connector={"line": {"color": "#94a3b8", "width": 1.5}},
        increasing={"marker": {"color": "#22c55e"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#0D47A1"}},
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#0D47A1")),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        showlegend=False,
        yaxis=dict(title="EUR", gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-20),
        margin=dict(l=20, r=20, t=60, b=40),
    )
    return fig

def bu_bar_chart(bu_names, budget_vals, actual_vals, title="Scostamento per Business Unit"):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Budget",
        x=bu_names,
        y=budget_vals,
        marker_color="#0D47A1",
        text=[fmt_eur(v) for v in budget_vals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Actual",
        x=bu_names,
        y=actual_vals,
        marker_color=[delta_color(a - b) for a, b in zip(actual_vals, budget_vals)],
        text=[fmt_eur(v) for v in actual_vals],
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#0D47A1")),
        barmode="group",
        height=380,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1),
        yaxis=dict(gridcolor="#f1f5f9"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig

def driver_chart(drivers, impacts):
    colors = [delta_color(v) for v in impacts]
    fig = go.Figure(go.Bar(
        y=drivers,
        x=impacts,
        orientation="h",
        marker_color=colors,
        text=[fmt_eur(v) for v in impacts],
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text="Impatto dei 9 Driver di Scostamento", font=dict(size=15, color="#0D47A1")),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="EUR", gridcolor="#f1f5f9"),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig

# ─── CSV Parser ───────────────────────────────────────────────────────────────

def parse_variance_csv(uploaded_file):
    """
    Formato CSV atteso (2 colonne: voce, valore):
    # commenti ignorati
    ricavi_budget,10000000
    ricavi_actual,9200000
    cogs_budget,6000000
    cogs_actual,5800000
    ...
    """
    lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    data = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                data[parts[0].strip().lower()] = float(parts[1].strip().replace(".", "").replace(",", "."))
            except ValueError:
                pass
    return data

def _v(data, key, default=0.0):
    return data.get(key, default)

# ─── Calcoli Waterfall ────────────────────────────────────────────────────────

def calc_waterfall_p_and_l(d):
    """Calcola la cascata Budget->Actual dal Gross Margin al Net Result."""
    ricavi_b = _v(d, "ricavi_budget")
    ricavi_a = _v(d, "ricavi_actual")
    cogs_b   = _v(d, "cogs_budget")
    cogs_a   = _v(d, "cogs_actual")
    gm_b = ricavi_b - cogs_b
    gm_a = ricavi_a - cogs_a

    opex_b = _v(d, "opex_budget")
    opex_a = _v(d, "opex_actual")
    ebitda_b = gm_b - opex_b
    ebitda_a = gm_a - opex_a

    da_b = _v(d, "ammortamenti_budget")
    da_a = _v(d, "ammortamenti_actual")
    ebit_b = ebitda_b - da_b
    ebit_a = ebitda_a - da_a

    fin_b = _v(d, "oneri_finanziari_budget")
    fin_a = _v(d, "oneri_finanziari_actual")
    ebt_b = ebit_b - fin_b
    ebt_a = ebit_a - fin_a

    tax_b = _v(d, "imposte_budget")
    tax_a = _v(d, "imposte_actual")
    net_b = ebt_b - tax_b
    net_a = ebt_a - tax_a

    return dict(
        ricavi_b=ricavi_b, ricavi_a=ricavi_a,
        gm_b=gm_b, gm_a=gm_a,
        ebitda_b=ebitda_b, ebitda_a=ebitda_a,
        ebit_b=ebit_b, ebit_a=ebit_a,
        net_b=net_b, net_a=net_a,
        da_b=da_b, da_a=da_a,
        fin_b=fin_b, fin_a=fin_a,
    )

# ─── PDF Export ───────────────────────────────────────────────────────────────

def generate_variance_pdf(company, period, res, bu_data, drivers):
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    def cl(t):
        return t.encode("latin-1", errors="replace").decode("latin-1")

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(13, 71, 161)
            self.rect(0, 0, 210, 22, "F")
            self.set_font("Helvetica", "B", 14)
            self.set_text_color(255, 255, 255)
            self.cell(0, 22, cl("NEXUS Finance Pro - Variance Analysis Report"), align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0, 0, 0)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, cl(f"NEXUS Finance Pro - Confidenziale - Pagina {self.page_no()}"), align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(15, 28, 15)

    # Titolo
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(13, 71, 161)
    pdf.ln(4)
    pdf.cell(0, 10, cl(f"Analisi Scostamenti Budget vs Actual — {company}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, cl(f"Periodo: {period}  |  Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    def section_title(t):
        pdf.set_fill_color(232, 240, 254)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(13, 71, 161)
        pdf.cell(0, 8, cl(f"  {t}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    def kpi_row(label, budget, actual, fill=False):
        delta = actual - budget
        pct = (delta / budget * 100) if budget != 0 else 0
        pdf.set_fill_color(248, 250, 255) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(65, 7, cl(label), fill=fill, border="B")
        pdf.cell(40, 7, cl(fmt_eur(budget)), fill=fill, border="B", align="R")
        pdf.cell(40, 7, cl(fmt_eur(actual)), fill=fill, border="B", align="R")
        sign = "+" if delta >= 0 else ""
        r, g, b = (34, 197, 94) if delta >= 0 else (239, 68, 68)
        pdf.set_text_color(r, g, b)
        pdf.cell(40, 7, cl(f"{sign}{fmt_eur(delta)} ({sign}{pct:.1f}%)"), fill=fill, border="B", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    # Sezione 1 — P&L Waterfall
    section_title("1. Conto Economico: Budget vs Actual")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(13, 71, 161)
    pdf.set_text_color(255, 255, 255)
    for h, w in [("Voce P&L", 65), ("Budget", 40), ("Actual", 40), ("Delta (+/-)", 40)]:
        pdf.cell(w, 7, cl(h), fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    rows = [
        ("Ricavi Netti",    res["ricavi_b"], res["ricavi_a"]),
        ("Gross Margin",    res["gm_b"],     res["gm_a"]),
        ("EBITDA",          res["ebitda_b"], res["ebitda_a"]),
        ("EBIT",            res["ebit_b"],   res["ebit_a"]),
        ("Risultato Netto", res["net_b"],    res["net_a"]),
    ]
    for i, (label, b, a) in enumerate(rows):
        kpi_row(label, b, a, fill=(i % 2 == 0))
    pdf.ln(6)

    # Sezione 2 — Business Unit
    section_title("2. Scostamento per Business Unit")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(13, 71, 161)
    pdf.set_text_color(255, 255, 255)
    for h, w in [("Business Unit", 65), ("Budget", 40), ("Actual", 40), ("Delta", 40)]:
        pdf.cell(w, 7, cl(h), fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    for i, (bu, b, a) in enumerate(bu_data):
        kpi_row(bu, b, a, fill=(i % 2 == 0))
    pdf.ln(6)

    # Sezione 3 — 9 Driver
    section_title("3. I 9 Driver di Scostamento")
    driver_names = [d[0] for d in drivers]
    driver_vals  = [d[1] for d in drivers]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(13, 71, 161)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 7, cl("Driver"), fill=True)
    pdf.cell(40, 7, cl("Impatto EUR"), fill=True, align="R")
    pdf.cell(30, 7, cl("Stato"), fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    for i, (name, val) in enumerate(zip(driver_names, driver_vals)):
        pdf.set_fill_color(248, 250, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(110, 7, cl(name), fill=(i % 2 == 0), border="B")
        sign = "+" if val >= 0 else ""
        r, g, b = (34, 197, 94) if val >= 0 else (239, 68, 68)
        pdf.set_text_color(r, g, b)
        pdf.cell(40, 7, cl(f"{sign}{fmt_eur(val)}"), fill=(i % 2 == 0), border="B", align="R")
        pdf.set_text_color(0, 0, 0)
        stato = "OK" if val >= 0 else "ATTENZIONE"
        pdf.cell(30, 7, cl(stato), fill=(i % 2 == 0), border="B", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Sezione 4 — Note legali
    section_title("4. Note Legali e Covenant")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    notes = [
        "Il presente report e stato prodotto da NEXUS Finance Pro ai sensi del D.Lgs. 14/2019 (CCII).",
        "L'analisi degli scostamenti e conforme agli standard Invitalia per il monitoraggio dei piani di risanamento.",
        "I dati riportati sono quelli inseriti dall'utente e hanno valore di reportistica gestionale.",
        "Per utilizzo in sede legale o bancaria, il documento deve essere corredato da relazione del revisore.",
        cl(f"Generato da: NEXUS Finance Pro v5.0 | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Utente: Admin"),
    ]
    for note in notes:
        pdf.cell(0, 6, cl(note), new_x="LMARGIN", new_y="NEXT")

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()

# ─── Default Data ─────────────────────────────────────────────────────────────

DEFAULT_COIN = {
    "ricavi_budget":             195_000_000,
    "ricavi_actual":             169_900_000,
    "cogs_budget":               120_000_000,
    "cogs_actual":               115_000_000,
    "opex_budget":                42_000_000,
    "opex_actual":                54_000_000,
    "ammortamenti_budget":        12_000_000,
    "ammortamenti_actual":        18_500_000,
    "oneri_finanziari_budget":     8_000_000,
    "oneri_finanziari_actual":    12_400_000,
    "imposte_budget":              3_000_000,
    "imposte_actual":                      0,
}

DEFAULT_BU = [
    ("B&B (Casa + Arredamento)", 62_000_000, 52_300_000),
    ("Casa (Accessori)",          55_000_000, 48_700_000),
    ("GMM (Moda/Lifestyle)",      48_000_000, 40_200_000),
    ("WHS (Warehouse Sale)",      18_000_000, 14_900_000),
    ("HB (Home Basics)",          8_000_000,  9_100_000),
    ("CNR (Resi/Rettifiche)",     4_000_000,  4_700_000),
]

DEFAULT_DRIVERS = [
    ("1. Ritardo AuCap (Golden Power + Anti Trust)",  -8_500_000),
    ("2. Negoziazioni fornitori - Concessioni",         2_100_000),
    ("3. Stralci debitoria fornitori",                  3_800_000),
    ("4. Scontistica accelerazione vendite/cassa",     -6_200_000),
    ("5. Negoziazioni GF - Linea Factor",              -1_900_000),
    ("6. Chiusure POS inattese (sicurezza)",            -3_100_000),
    ("7. Ammortamenti extra (errore calc. parametrico)", -6_500_000),
    ("8. Riduzione ingressi (traffico clienti)",        -7_300_000),
    ("9. Svalutazioni magazzino + ritardo WHS",         -4_800_000),
]

# ─── Render Main ──────────────────────────────────────────────────────────────

def show_variance_analysis():
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0D47A1,#1565C0);
                border-radius:16px; padding:24px 28px; margin-bottom:24px;'>
        <div style='font-size:28px; font-weight:800; color:white;'>
            📊 Variance Analysis Suite
        </div>
        <div style='font-size:14px; color:rgba(255,255,255,0.85); margin-top:6px;'>
            Analisi Scostamenti Budget vs Actual &nbsp;|&nbsp;
            Waterfall P&amp;L &nbsp;|&nbsp; Breakdown Business Unit &nbsp;|&nbsp;
            9 Driver di Scostamento &nbsp;|&nbsp; Export Invitalia-ready
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⚡ Carica & Analizza", "📝 Inserimento Manuale"])

    # ── TAB 1: Upload CSV ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📂 Carica CSV Budget vs Actual")
        st.info("""
**Formato CSV (2 colonne: voce, valore)**
```
# Ricavi
ricavi_budget,195000000
ricavi_actual,169900000
cogs_budget,120000000
cogs_actual,115000000
opex_budget,42000000
opex_actual,54000000
ammortamenti_budget,12000000
ammortamenti_actual,18500000
oneri_finanziari_budget,8000000
oneri_finanziari_actual,12400000
imposte_budget,3000000
imposte_actual,0
```
        """)
        uploaded = st.file_uploader("Carica CSV Variance", type=["csv"], key="var_csv")
        if uploaded:
            raw = parse_variance_csv(uploaded)
            if raw:
                st.session_state["var_data"] = raw
                st.success(f"✅ Caricati {len(raw)} valori dal CSV")
            else:
                st.error("❌ CSV non riconosciuto — verifica il formato")

    # ── TAB 2: Form Manuale ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 📝 Inserimento Manuale Budget vs Actual")

        d = st.session_state.get("var_data", DEFAULT_COIN)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏢 Dati Azienda")
            company_name = st.text_input("Nome Azienda", value="COIN SPA", key="var_company")
            period = st.text_input("Periodo", value="Esercizio 2025", key="var_period")
            st.markdown("#### 💰 Ricavi")
            ricavi_b = st.number_input("Ricavi Budget (EUR)", value=float(d.get("ricavi_budget", 195_000_000)), step=100_000.0, format="%.0f", key="vb_ricavi_b")
            ricavi_a = st.number_input("Ricavi Actual (EUR)", value=float(d.get("ricavi_actual", 169_900_000)), step=100_000.0, format="%.0f", key="vb_ricavi_a")
            st.markdown("#### 🏭 COGS (Costo del Venduto)")
            cogs_b = st.number_input("COGS Budget (EUR)", value=float(d.get("cogs_budget", 120_000_000)), step=100_000.0, format="%.0f", key="vb_cogs_b")
            cogs_a = st.number_input("COGS Actual (EUR)", value=float(d.get("cogs_actual", 115_000_000)), step=100_000.0, format="%.0f", key="vb_cogs_a")
            st.markdown("#### 📉 OPEX (Costi Operativi)")
            opex_b = st.number_input("OPEX Budget (EUR)", value=float(d.get("opex_budget", 42_000_000)), step=100_000.0, format="%.0f", key="vb_opex_b")
            opex_a = st.number_input("OPEX Actual (EUR)", value=float(d.get("opex_actual", 54_000_000)), step=100_000.0, format="%.0f", key="vb_opex_a")

        with col2:
            st.markdown("#### 🔧 Ammortamenti & Svalutazioni")
            da_b = st.number_input("Ammortamenti Budget (EUR)", value=float(d.get("ammortamenti_budget", 12_000_000)), step=100_000.0, format="%.0f", key="vb_da_b")
            da_a = st.number_input("Ammortamenti Actual (EUR)", value=float(d.get("ammortamenti_actual", 18_500_000)), step=100_000.0, format="%.0f", key="vb_da_a")
            st.markdown("#### 🏦 Oneri Finanziari")
            fin_b = st.number_input("Oneri Finanziari Budget (EUR)", value=float(d.get("oneri_finanziari_budget", 8_000_000)), step=100_000.0, format="%.0f", key="vb_fin_b")
            fin_a = st.number_input("Oneri Finanziari Actual (EUR)", value=float(d.get("oneri_finanziari_actual", 12_400_000)), step=100_000.0, format="%.0f", key="vb_fin_a")
            st.markdown("#### 🧾 Imposte")
            tax_b = st.number_input("Imposte Budget (EUR)", value=float(d.get("imposte_budget", 3_000_000)), step=100_000.0, format="%.0f", key="vb_tax_b")
            tax_a = st.number_input("Imposte Actual (EUR)", value=float(d.get("imposte_actual", 0)), step=100_000.0, format="%.0f", key="vb_tax_a")

        # Assembla dati
        data_input = {
            "ricavi_budget": ricavi_b, "ricavi_actual": ricavi_a,
            "cogs_budget": cogs_b, "cogs_actual": cogs_a,
            "opex_budget": opex_b, "opex_actual": opex_a,
            "ammortamenti_budget": da_b, "ammortamenti_actual": da_a,
            "oneri_finanziari_budget": fin_b, "oneri_finanziari_actual": fin_a,
            "imposte_budget": tax_b, "imposte_actual": tax_a,
        }
        st.session_state["var_data_form"] = data_input
        st.session_state["var_company_name"] = company_name

    # ── ANALISI (sotto entrambe le tab) ───────────────────────────────────────
    st.markdown("---")

    # Prendi dati (form ha precedenza su CSV se compilati)
    d_use = st.session_state.get("var_data_form", DEFAULT_COIN)
    company_name = st.session_state.get("var_company_name", "La tua Azienda")
    period = st.session_state.get("var_period", "Esercizio 2025")

    res = calc_waterfall_p_and_l(d_use)

    # ── KPI Summary ───────────────────────────────────────────────────────────
    st.markdown("## 📊 Risultati Analisi Scostamenti")
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        ("Ricavi", res["ricavi_b"], res["ricavi_a"]),
        ("Gross Margin", res["gm_b"], res["gm_a"]),
        ("EBITDA", res["ebitda_b"], res["ebitda_a"]),
        ("EBIT", res["ebit_b"], res["ebit_a"]),
        ("Risultato Netto", res["net_b"], res["net_a"]),
    ]
    for col, (label, bv, av) in zip([c1, c2, c3, c4, c5], kpis):
        delta = av - bv
        pct = (delta / bv * 100) if bv != 0 else 0
        color = "#22c55e" if delta >= 0 else "#ef4444"
        icon = "▲" if delta >= 0 else "▼"
        col.markdown(f"""
        <div style='background:#f8faff; border-radius:12px; padding:14px 12px;
                    border:1px solid #e3eafc; box-shadow:0 2px 8px rgba(13,71,161,0.06);
                    text-align:center;'>
            <div style='font-size:11px; color:#64748b; font-weight:600;'>{label}</div>
            <div style='font-size:14px; font-weight:800; color:#0D47A1; margin:4px 0;'>{fmt_eur(av)}</div>
            <div style='font-size:11px; color:{color}; font-weight:700;'>
                {icon} {fmt_eur(delta)} ({'+' if pct>=0 else ''}{pct:.1f}%)
            </div>
            <div style='font-size:10px; color:#94a3b8;'>Budget: {fmt_eur(bv)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Waterfall P&L ─────────────────────────────────────────────────────────
    st.markdown("### 🌊 Waterfall: dal Gross Margin al Risultato Netto")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**📘 Budget**")
        wf_labels_b = ["Budget Ricavi", "- COGS", "= Gross Margin", "- OPEX", "= EBITDA", "- Amm.ti", "= EBIT", "- Oneri Fin.", "= Ris. Netto"]
        wf_values_b = [
            res["ricavi_b"],
            -(res["ricavi_b"] - res["gm_b"]),
            res["gm_b"],
            -d_use["opex_budget"],
            res["ebitda_b"],
            -d_use["ammortamenti_budget"],
            res["ebit_b"],
            -d_use["oneri_finanziari_budget"],
            res["net_b"],
        ]
        # Misure corrette
        measures_b = ["absolute", "relative", "total", "relative", "total", "relative", "total", "relative", "total"]
        fig_b = go.Figure(go.Waterfall(
            measure=measures_b,
            x=wf_labels_b, y=wf_values_b,
            text=[fmt_eur(v) for v in wf_values_b],
            textposition="outside",
            connector={"line": {"color": "#94a3b8"}},
            increasing={"marker": {"color": "#22c55e"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#0D47A1"}},
        ))
        fig_b.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
                             showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
                             yaxis=dict(gridcolor="#f1f5f9"), xaxis=dict(tickangle=-30))
        st.plotly_chart(fig_b, use_container_width=True)

    with col_b:
        st.markdown("**📕 Actual**")
        wf_labels_a = ["Actual Ricavi", "- COGS", "= Gross Margin", "- OPEX", "= EBITDA", "- Amm.ti", "= EBIT", "- Oneri Fin.", "= Ris. Netto"]
        wf_values_a = [
            res["ricavi_a"],
            -(res["ricavi_a"] - res["gm_a"]),
            res["gm_a"],
            -d_use["opex_actual"],
            res["ebitda_a"],
            -d_use["ammortamenti_actual"],
            res["ebit_a"],
            -d_use["oneri_finanziari_actual"],
            res["net_a"],
        ]
        measures_a = ["absolute", "relative", "total", "relative", "total", "relative", "total", "relative", "total"]
        fig_a = go.Figure(go.Waterfall(
            measure=measures_a,
            x=wf_labels_a, y=wf_values_a,
            text=[fmt_eur(v) for v in wf_values_a],
            textposition="outside",
            connector={"line": {"color": "#94a3b8"}},
            increasing={"marker": {"color": "#22c55e"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#1565C0"}},
        ))
        fig_a.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
                             showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
                             yaxis=dict(gridcolor="#f1f5f9"), xaxis=dict(tickangle=-30))
        st.plotly_chart(fig_a, use_container_width=True)

    # ── Waterfall Scostamento ─────────────────────────────────────────────────
    st.markdown("### 🔻 Waterfall Scostamento (Delta Budget → Actual)")
    delta_gm   = res["gm_a"] - res["gm_b"]
    delta_opex = -(d_use["opex_actual"] - d_use["opex_budget"])
    delta_da   = -(d_use["ammortamenti_actual"] - d_use["ammortamenti_budget"])
    delta_fin  = -(d_use["oneri_finanziari_actual"] - d_use["oneri_finanziari_budget"])
    delta_tax  = -(d_use["imposte_actual"] - d_use["imposte_budget"])

    wf_d_labels = ["Gross Margin Budget", "Delta Ricavi+Mix", "Delta OPEX", "Delta Ammortamenti", "Delta Oneri Fin.", "Delta Imposte", "Risultato Netto Actual"]
    wf_d_values = [
        res["gm_b"],
        res["gm_a"] - res["gm_b"],
        delta_opex,
        delta_da,
        delta_fin,
        delta_tax,
        res["net_a"],
    ]
    wf_d_measures = ["absolute", "relative", "relative", "relative", "relative", "relative", "total"]
    fig_d = go.Figure(go.Waterfall(
        measure=wf_d_measures,
        x=wf_d_labels, y=wf_d_values,
        text=[fmt_eur(v) for v in wf_d_values],
        textposition="outside",
        connector={"line": {"color": "#94a3b8"}},
        increasing={"marker": {"color": "#22c55e"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#0D47A1"}},
    ))
    fig_d.update_layout(
        height=400, plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, margin=dict(l=10, r=10, t=30, b=10),
        yaxis=dict(title="EUR", gridcolor="#f1f5f9"),
        xaxis=dict(tickangle=-20),
    )
    st.plotly_chart(fig_d, use_container_width=True)

    # ── Business Unit ─────────────────────────────────────────────────────────
    st.markdown("### 🏢 Scostamento per Business Unit")
    st.markdown("*Inserisci i dati per le singole BU (puoi modificarli)*")

    bu_data = []
    bu_names_def = ["B&B (Casa+Arred.)", "Casa (Accessori)", "GMM (Moda/Lifestyle)", "WHS (Warehouse)", "HB (Home Basics)", "CNR (Resi)"]
    bu_b_def = [62_000_000, 55_000_000, 48_000_000, 18_000_000, 8_000_000, 4_000_000]
    bu_a_def = [52_300_000, 48_700_000, 40_200_000, 14_900_000, 9_100_000, 4_700_000]

    bu_cols = st.columns(3)
    bu_inputs = []
    for i, (name, bv, av) in enumerate(zip(bu_names_def, bu_b_def, bu_a_def)):
        with bu_cols[i % 3]:
            with st.expander(f"📦 {name}", expanded=False):
                bval = st.number_input(f"Budget", value=float(bv), step=100_000.0, format="%.0f", key=f"bu_b_{i}")
                aval = st.number_input(f"Actual", value=float(av), step=100_000.0, format="%.0f", key=f"bu_a_{i}")
                bu_inputs.append((name, bval, aval))

    bu_names = [x[0] for x in bu_inputs]
    bu_bvals = [x[1] for x in bu_inputs]
    bu_avals = [x[2] for x in bu_inputs]
    bu_data  = bu_inputs

    fig_bu = bu_bar_chart(bu_names, bu_bvals, bu_avals)
    st.plotly_chart(fig_bu, use_container_width=True)

    # Tabella BU
    df_bu = pd.DataFrame({
        "Business Unit": bu_names,
        "Budget (EUR)": [fmt_eur(v) for v in bu_bvals],
        "Actual (EUR)": [fmt_eur(v) for v in bu_avals],
        "Delta (EUR)": [fmt_eur(a - b) for a, b in zip(bu_avals, bu_bvals)],
        "Delta %": [fmt_pct((a - b) / b * 100) if b != 0 else "N/A" for a, b in zip(bu_avals, bu_bvals)],
        "Stato": ["✅ OK" if a >= b else "⚠️ Sotto budget" for a, b in zip(bu_avals, bu_bvals)],
    })
    st.dataframe(df_bu, use_container_width=True, hide_index=True)

    # ── 9 Driver ──────────────────────────────────────────────────────────────
    st.markdown("### 🔍 I 9 Driver di Scostamento")
    st.markdown("*Quantifica l'impatto di ogni causa di scostamento (positivo = recupero, negativo = perdita)*")

    driver_defaults = DEFAULT_DRIVERS
    driver_inputs = []
    dr_cols = st.columns(2)
    for i, (name, val) in enumerate(driver_defaults):
        with dr_cols[i % 2]:
            dv = st.number_input(
                f"Driver {i+1}: {name[:45]}",
                value=float(val),
                step=100_000.0,
                format="%.0f",
                key=f"dr_{i}"
            )
            driver_inputs.append((name, dv))

    driver_names = [d[0] for d in driver_inputs]
    driver_vals  = [d[1] for d in driver_inputs]
    fig_dr = driver_chart(driver_names, driver_vals)
    st.plotly_chart(fig_dr, use_container_width=True)

    # Totale driver
    total_driver = sum(driver_vals)
    st.markdown(f"""
    <div style='background:{"#dcfce7" if total_driver >= 0 else "#fee2e2"};
                border-radius:10px; padding:14px 18px; margin:8px 0;
                border-left:4px solid {"#22c55e" if total_driver >= 0 else "#ef4444"};'>
        <b>Impatto Totale dei 9 Driver: {fmt_eur(total_driver)}</b>
        {" — Risultato complessivo positivo ✅" if total_driver >= 0 else " — Risultato complessivo negativo ⚠️"}
    </div>
    """, unsafe_allow_html=True)

    # ── Semaforo Covenant ─────────────────────────────────────────────────────
    st.markdown("### 🚦 Semaforo Covenant Bancari & Invitalia")

    ebitda_margin_b = (res["ebitda_b"] / res["ricavi_b"] * 100) if res["ricavi_b"] != 0 else 0
    ebitda_margin_a = (res["ebitda_a"] / res["ricavi_a"] * 100) if res["ricavi_a"] != 0 else 0
    rev_drop = ((res["ricavi_a"] - res["ricavi_b"]) / res["ricavi_b"] * 100) if res["ricavi_b"] != 0 else 0
    gm_margin_a = (res["gm_a"] / res["ricavi_a"] * 100) if res["ricavi_a"] != 0 else 0

    covenants = [
        ("EBITDA Margin Actual", ebitda_margin_a, "%",
         "OK" if ebitda_margin_a > 5 else ("ATTENZIONE" if ebitda_margin_a > 0 else "CRITICO"),
         f"Budget: {ebitda_margin_b:.1f}%"),
        ("Scostamento Ricavi vs Budget", rev_drop, "%",
         "OK" if rev_drop > -5 else ("ATTENZIONE" if rev_drop > -15 else "CRITICO"),
         "Soglia covenant tipica: -15%"),
        ("Gross Margin % Actual", gm_margin_a, "%",
         "OK" if gm_margin_a > 25 else ("ATTENZIONE" if gm_margin_a > 15 else "CRITICO"),
         "Soglia minima retail: 20%"),
        ("Ammortamenti: Delta vs Budget",
         ((d_use["ammortamenti_actual"] - d_use["ammortamenti_budget"]) / d_use["ammortamenti_budget"] * 100) if d_use["ammortamenti_budget"] != 0 else 0,
         "%",
         "OK" if d_use["ammortamenti_actual"] <= d_use["ammortamenti_budget"] * 1.1 else "ATTENZIONE",
         "Errore calc. parametrico dichiarato"),
    ]

    cov_cols = st.columns(4)
    for col, (label, val, unit, stato, note) in zip(cov_cols, covenants):
        bg = "#dcfce7" if stato == "OK" else ("#fef3c7" if stato == "ATTENZIONE" else "#fee2e2")
        icon = "✅" if stato == "OK" else ("⚠️" if stato == "ATTENZIONE" else "🔴")
        col.markdown(f"""
        <div style='background:{bg}; border-radius:12px; padding:14px 12px;
                    border:1px solid #e3eafc; text-align:center;'>
            <div style='font-size:11px; color:#64748b; font-weight:600;'>{label}</div>
            <div style='font-size:20px; font-weight:800; color:#0D47A1; margin:6px 0;'>
                {val:.1f}{unit}
            </div>
            <div style='font-size:14px; font-weight:700;'>{icon} {stato}</div>
            <div style='font-size:10px; color:#94a3b8; margin-top:4px;'>{note}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Export PDF ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Export Report Invitalia-Ready")

    col_pdf1, col_pdf2 = st.columns([1, 3])
    with col_pdf1:
        if st.button("📄 Genera Report PDF", type="primary", key="var_pdf_btn"):
            with st.spinner("Generazione PDF in corso..."):
                pdf_bytes = generate_variance_pdf(company_name, period, res, bu_data, driver_inputs)
                if pdf_bytes:
                    st.session_state["var_pdf"] = pdf_bytes
                    st.success("✅ PDF pronto!")
                else:
                    st.error("❌ Errore generazione PDF")

    if "var_pdf" in st.session_state:
        fname = f"Variance_Analysis_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m')}.pdf"
        st.download_button(
            label="📥 Scarica Report PDF (Invitalia-Ready)",
            data=st.session_state["var_pdf"],
            file_name=fname,
            mime="application/pdf",
            key="var_pdf_download"
        )
        st.info("💡 Il PDF include: Waterfall P&L, BU Breakdown, 9 Driver, Covenant — pronto per Invitalia/Banche")
