import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Coin-Nexus | Financial Intelligence",
    layout="wide",
    page_icon="🏦"
)

# =========================
# HELPERS - SCORE ENGINE
# =========================

def compute_kpis(df):

    # Safe check colonne base
    required = ['ricavi', 'costi', 'costi_fissi', 'costi_variabili',
                'attivo_corrente', 'passivo_corrente', 'debiti', 'cash']

    for col in required:
        if col not in df.columns:
            df[col] = 0

    ricavi = df["ricavi"].sum()
    costi = df["costi"].sum()
    costi_fissi = df["costi_fissi"].sum()
    costi_variabili = df["costi_variabili"].sum()

    attivo_corrente = df["attivo_corrente"].sum()
    passivo_corrente = df["passivo_corrente"].sum()
    debiti = df["debiti"].sum()

    ebitda = ricavi - costi
    ebitda_margin = ebitda / ricavi if ricavi else 0

    current_ratio = attivo_corrente / passivo_corrente if passivo_corrente else 0
    debt_ratio = debiti / ricavi if ricavi else 0

    variable_ratio = costi_variabili / ricavi if ricavi else 0
    bep = costi_fissi / (1 - variable_ratio) if variable_ratio < 1 else ricavi
    safety_margin = (ricavi - bep) / ricavi if ricavi else 0

    return {
        "ricavi": ricavi,
        "costi": costi,
        "ebitda": ebitda,
        "ebitda_margin": ebitda_margin,
        "current_ratio": current_ratio,
        "debt_ratio": debt_ratio,
        "bep": bep,
        "safety_margin": safety_margin
    }


def coin_nexus_score(kpi):

    score = 0

    # Redditività
    if kpi["ebitda_margin"] > 0.20:
        score += 30
    elif kpi["ebitda_margin"] > 0.10:
        score += 20
    elif kpi["ebitda_margin"] > 0:
        score += 10

    # Liquidità
    if kpi["current_ratio"] > 1.8:
        score += 25
    elif kpi["current_ratio"] > 1.2:
        score += 15
    else:
        score += 5

    # Debito
    if kpi["debt_ratio"] < 0.3:
        score += 20
    elif kpi["debt_ratio"] < 0.6:
        score += 10
    else:
        score += 5

    # Stabilità
    if kpi["safety_margin"] > 0.3:
        score += 15
    elif kpi["safety_margin"] > 0.1:
        score += 8
    else:
        score += 2

    return score


def risk_label(score):

    if score >= 80:
        return "🟢 ALTA AFFIDABILITÀ - CREDITO CONSIGLIATO"
    elif score >= 60:
        return "🟡 AFFIDABILITÀ MEDIA - CONDIZIONATO"
    elif score >= 40:
        return "🟠 RISCHIO MODERATO"
    else:
        return "🔴 ALTO RISCHIO"


# =========================
# PDF REPORT
# =========================

class Report(FPDF):

    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "COIN-NEXUS FINANCIAL REPORT", ln=True, align="C")
        self.ln(5)

    def section(self, title, text):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(3)


# =========================
# UI
# =========================

st.title("🏦 Coin-Nexus | Financial Intelligence Terminal")

uploaded = st.file_uploader("Carica file ERP (CSV / XLSX)", type=["csv", "xlsx"])

if uploaded:

    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.subheader("📊 Dati caricati")
    st.dataframe(df.head())

    kpi = compute_kpis(df)
    score = coin_nexus_score(kpi)
    label = risk_label(score)

    # =========================
    # KPI DASHBOARD
    # =========================
    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ricavi", f"€ {kpi['ricavi']:,.0f}")
    c2.metric("EBITDA", f"€ {kpi['ebitda']:,.0f}")
    c3.metric("Break Even", f"€ {kpi['bep']:,.0f}")
    c4.metric("Score", f"{score}/100")

    st.success(label)

    # =========================
    # CHART
    # =========================

    st.subheader("📈 Struttura Economica")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Ricavi", "Costi", "EBITDA"],
        y=[kpi["ricavi"], kpi["costi"], kpi["ebitda"]],
        marker_color=["green", "red", "blue"]
    ))

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # KPI TABLE
    # =========================

    st.subheader("📌 Indicatori Finanziari")

    st.table(pd.DataFrame({
        "KPI": [
            "EBITDA Margin",
            "Current Ratio",
            "Debt Ratio",
            "Safety Margin"
        ],
        "Valore": [
            round(kpi["ebitda_margin"], 3),
            round(kpi["current_ratio"], 2),
            round(kpi["debt_ratio"], 2),
            round(kpi["safety_margin"], 2)
        ]
    }))

    # =========================
    # PDF EXPORT
    # =========================

    if st.button("📥 Genera Report PDF"):

        pdf = Report()
        pdf.add_page()

        pdf.section(
            "Executive Summary",
            f"Coin-Nexus Score: {score}/100\n{label}"
        )

        pdf.section(
            "Financial Overview",
            f"Ricavi: {kpi['ricavi']}\nEBITDA: {kpi['ebitda']}"
        )

        pdf.section(
            "Risk Analysis",
            f"Debt Ratio: {kpi['debt_ratio']}\nSafety Margin: {kpi['safety_margin']}"
        )

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            "Scarica PDF",
            data=pdf_bytes,
            file_name="coin_nexus_report.pdf",
            mime="application/pdf"
        )

        st.success("Report generato con successo")
