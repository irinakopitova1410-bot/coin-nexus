"""
ESG Scoring Module — Environmental, Social, Governance
Rating sostenibilità per accesso al credito bancario (EBA Guidelines 2026)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io

from utils.ui_kit import page_header


# ─── Pesi ESG (EBA Guidelines on Loan Origination) ───────────────────────────
PESI = {"E": 0.35, "S": 0.35, "G": 0.30}

DOMANDE_E = [
    ("energia_rinnovabile", "% energia da fonti rinnovabili", 0, 100, 20, "%"),
    ("emissioni_co2", "Emissioni CO₂ (ton/M€ fatturato)", 0, 500, 150, "ton"),
    ("certificazione_iso14001", "Certificazione ISO 14001", 0, 1, 0, "bool"),
    ("piano_riduzione_emissioni", "Piano formale riduzione emissioni", 0, 1, 0, "bool"),
    ("rifiuti_differenziati", "% rifiuti differenziati/riciclati", 0, 100, 30, "%"),
    ("consumo_acqua", "Efficienza idrica (sistemi risparmio acqua)", 0, 1, 0, "bool"),
]

DOMANDE_S = [
    ("parita_genere", "% donne in posizioni manageriali", 0, 100, 20, "%"),
    ("infortuni_zero", "Infortuni negli ultimi 3 anni = 0", 0, 1, 0, "bool"),
    ("formazione_ore", "Ore formazione annua per dipendente", 0, 80, 10, "ore"),
    ("welfare_aziendale", "Piano welfare aziendale attivo", 0, 1, 0, "bool"),
    ("ccnl_applicato", "CCNL applicato correttamente", 0, 1, 1, "bool"),
    ("supply_chain_etica", "Fornitori con codice etico verificato", 0, 1, 0, "bool"),
]

DOMANDE_G = [
    ("cda_indipendenti", "% amministratori indipendenti in CDA", 0, 100, 20, "%"),
    ("revisione_esterna", "Revisione contabile esterna certificata", 0, 1, 0, "bool"),
    ("piano_anticorruzione", "Piano anticorruzione e compliance D.Lgs. 231", 0, 1, 0, "bool"),
    ("politica_remunerazione", "Politica remunerazione trasparente", 0, 1, 0, "bool"),
    ("whistleblowing", "Sistema whistleblowing attivo (D.Lgs. 24/2023)", 0, 1, 0, "bool"),
    ("rendicontazione_dnf", "Rendicontazione non finanziaria (DNF/ESRS)", 0, 1, 0, "bool"),
]


# ─── Calcolo Score ESG ────────────────────────────────────────────────────────
def normalizza(valore, min_v, max_v, tipo="normal"):
    """Normalizza il valore in [0,100]."""
    if tipo == "bool":
        return 100.0 if valore >= 1 else 0.0
    if max_v == min_v:
        return 50.0
    norm = (valore - min_v) / (max_v - min_v) * 100
    return max(0.0, min(100.0, norm))


def calcola_score_pillar(risposte: dict, domande: list) -> dict:
    punteggi = []
    for (chiave, label, min_v, max_v, default, tipo) in domande:
        val = risposte.get(chiave, default)
        if tipo == "bool":
            norm = 100.0 if val else 0.0
        elif chiave == "emissioni_co2":
            # Inverso: meno emissioni → punteggio più alto
            norm = 100.0 - normalizza(val, min_v, max_v)
        else:
            norm = normalizza(val, min_v, max_v, tipo)
        punteggi.append({"label": label, "score": round(norm, 1)})
    media = sum(p["score"] for p in punteggi) / len(punteggi)
    return {"score": round(media, 1), "dettaglio": punteggi}


def calcola_esg_totale(dati_e: dict, dati_s: dict, dati_g: dict) -> dict:
    e = calcola_score_pillar(dati_e, DOMANDE_E)
    s = calcola_score_pillar(dati_s, DOMANDE_S)
    g = calcola_score_pillar(dati_g, DOMANDE_G)
    totale = round(
        e["score"] * PESI["E"] +
        s["score"] * PESI["S"] +
        g["score"] * PESI["G"], 1
    )
    rating = (
        "AAA 🌿" if totale >= 85 else
        "AA ✅"  if totale >= 70 else
        "A 🔵"   if totale >= 55 else
        "BBB 🟡" if totale >= 40 else
        "BB 🟠"  if totale >= 25 else
        "B 🔴"
    )
    impatto_credito = (
        "+15–25% capacità credito" if totale >= 70 else
        "+5–10% capacità credito"  if totale >= 55 else
        "Nessun bonus ESG"         if totale >= 40 else
        "-10% capacità credito (rischio ESG)"
    )
    return {
        "E": e, "S": s, "G": g,
        "totale": totale, "rating": rating,
        "impatto_credito": impatto_credito
    }


# ─── Grafici ─────────────────────────────────────────────────────────────────
def grafico_gauge_esg(score: float, label: str) -> go.Figure:
    color = "#16A34A" if score >= 70 else "#D97706" if score >= 40 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": label, "font": {"color": "#0B1230", "size": 14}},
        number={"suffix": "/100", "font": {"color": color, "size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#64748b"},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,0.15)"},
                {"range": [40, 70], "color": "rgba(245,158,11,0.15)"},
                {"range": [70, 100],"color": "rgba(34,197,94,0.15)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score}
        }
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#0B1230"))
    return fig


def grafico_radar_esg(risultati: dict) -> go.Figure:
    cats = ["Environmental", "Social", "Governance"]
    vals = [risultati["E"]["score"], risultati["S"]["score"], risultati["G"]["score"]]
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(34,197,94,0.2)",
        line=dict(color="#16A34A", width=2),
        name="ESG Score"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="🌿 Profilo ESG",
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0B1230"),
        showlegend=False
    )
    return fig


def grafico_benchmark(score: float) -> go.Figure:
    categorie = ["La tua azienda", "PMI Media Italia", "PMI Virtuosa", "Standard bancario"]
    valori = [score, 42, 72, 55]
    colori = ["#6366f1", "#94a3b8", "#16A34A", "#D97706"]
    fig = go.Figure(go.Bar(
        x=valori, y=categorie,
        orientation="h",
        marker_color=colori,
        text=[f"{v}/100" for v in valori],
        textposition="outside"
    ))
    fig.update_layout(
        title="📊 Benchmark vs mercato",
        xaxis=dict(range=[0, 120]),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0B1230")
    )
    return fig


# ─── UI ──────────────────────────────────────────────────────────────────────
def show_esg_scoring():
    page_header(
        kicker="Sostenibilità · Questionario gestionale",
        title="ESG",
        highlight="Scoring",
        subtitle="Environmental · Social · Governance — autovalutazione orientativa, non certificazione o rating bancario.",
    )

    st.caption("Pesi e soglie del punteggio sono interni a NEXUS e non sono prescritti o validati dall’EBA. "
               "Il risultato non attesta conformità CSRD, Tassonomia UE o idoneità a finanziamenti.")
    with st.expander("ℹ️ Come interpretare questo punteggio ESG", expanded=False):
        st.markdown("""
        **Il punteggio organizza le risposte al questionario e aiuta a individuare aree da approfondire.**

        - Un punteggio elevato non garantisce credito, tassi migliori o accesso a prodotti green.
        - Gli obblighi di rendicontazione dipendono da impresa, dimensioni, ambito e norme applicabili.
        - Per attestazioni, requisiti di finanziamento e conformità occorrono documenti verificati e una valutazione professionale.
        """)

    tab_upload, tab_manuale = st.tabs(["⚡ Carica & Analizza", "📝 Questionario ESG"])

    with tab_upload:
        _tab_upload_esg()
    with tab_manuale:
        _tab_manuale_esg()


def _esegui_analisi_esg(dati_e, dati_s, dati_g, azienda="Azienda", key_prefix="esg_upload_result"):
    risultati = calcola_esg_totale(dati_e, dati_s, dati_g)
    score_tot = risultati["totale"]
    rating = risultati["rating"]

    st.markdown(f"---\n### 🌿 ESG Report — **{azienda}**")

    # Score totale prominente
    col_r, col_e, col_s, col_g = st.columns(4)
    with col_r:
        color = "#16A34A" if score_tot >= 70 else "#D97706" if score_tot >= 40 else "#ef4444"
        st.markdown(f"""
        <div style='text-align:center; background:#FFFFFF; border-radius:12px; padding:1rem;
                    border: 1px solid #E6EAF2; border-top: 3px solid {color};
                    box-shadow: 0 1px 3px rgba(11,18,48,0.06);'>
            <div style='font-size:2.5rem; font-weight:700; color:{color};'>{score_tot}</div>
            <div style='color:#5A6478; font-size:0.9rem;'>ESG Score /100</div>
            <div style='color:{color}; font-weight:600; font-size:1.1rem;'>{rating}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_e:
        st.plotly_chart(grafico_gauge_esg(risultati["E"]["score"], "🌍 Environmental"), use_container_width=True, key=f"{key_prefix}_e")
    with col_s:
        st.plotly_chart(grafico_gauge_esg(risultati["S"]["score"], "👥 Social"), use_container_width=True, key=f"{key_prefix}_s")
    with col_g:
        st.plotly_chart(grafico_gauge_esg(risultati["G"]["score"], "⚖️ Governance"), use_container_width=True, key=f"{key_prefix}_g")

    # Impatto credito
    impatto_color = "#16A34A" if score_tot >= 55 else "#D97706" if score_tot >= 40 else "#ef4444"
    st.markdown(f"""
    <div style='background:#FFFFFF; border: 1px solid #E6EAF2; border-left: 4px solid {impatto_color};
                padding: 1rem; border-radius: 0 8px 8px 0; margin: 1rem 0;
                box-shadow: 0 1px 3px rgba(11,18,48,0.05);'>
        <b style='color:{impatto_color};'>💰 Impatto sul credito bancario:</b>
        <span style='color:#0B1230;'> {risultati["impatto_credito"]}</span>
    </div>
    """, unsafe_allow_html=True)

    # Grafici
    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        st.plotly_chart(grafico_radar_esg(risultati), use_container_width=True, key=f"{key_prefix}_radar")
    with col_g2:
        st.plotly_chart(grafico_benchmark(score_tot), use_container_width=True, key=f"{key_prefix}_benchmark")

    # Raccomandazioni
    st.markdown("### 💡 Piano di Miglioramento ESG")
    raccomandazioni = []
    if risultati["E"]["score"] < 60:
        raccomandazioni.append(("🌍 Environmental", "Installa pannelli fotovoltaici o acquista certificati GO (Garanzie di Origine) → +15 punti E", "Alta"))
        raccomandazioni.append(("🌍 Environmental", "Ottieni certificazione ISO 14001 → segnale forte per le banche", "Media"))
    if risultati["S"]["score"] < 60:
        raccomandazioni.append(("👥 Social", "Aumenta la % di donne in management → accesso a finanziamenti BEI parità di genere", "Alta"))
        raccomandazioni.append(("👥 Social", "Attiva piano welfare aziendale → riduce turnover e migliora rating S", "Media"))
    if risultati["G"]["score"] < 60:
        raccomandazioni.append(("⚖️ Governance", "Adotta Modello Organizzativo 231 → obbligo per molti bandi pubblici", "Alta"))
        raccomandazioni.append(("⚖️ Governance", "Implementa sistema whistleblowing (D.Lgs. 24/2023) → obbligo legale >50 dipendenti", "Alta"))
    if not raccomandazioni:
        st.success("🏆 Ottimo profilo ESG! Sei posizionato per i migliori tassi sui Green Loan.")
    else:
        for area, azione, priorita in raccomandazioni[:5]:
            color_p = "#ef4444" if priorita == "Alta" else "#D97706"
            st.markdown(f"- **{area}** — {azione} <span style='color:{color_p};'>({priorita} priorità)</span>",
                        unsafe_allow_html=True)

    # Export
    st.markdown("---")
    export_data = {
        "Pillar": ["Environmental", "Social", "Governance", "TOTALE"],
        "Score": [risultati["E"]["score"], risultati["S"]["score"],
                  risultati["G"]["score"], score_tot],
        "Rating": ["-", "-", "-", rating]
    }
    csv_out = pd.DataFrame(export_data).to_csv(index=False)
    st.download_button("📥 Scarica Report ESG (CSV)", csv_out,
                      f"ESG_{azienda.replace(' ','_')}.csv", "text/csv",
                      use_container_width=True, key=f"{key_prefix}_csv")


def _tab_upload_esg():
    st.markdown("""
    <div style='background: rgba(22,101,52,0.15); border: 1px solid rgba(34,197,94,0.3);
                border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
        <b>⚡ Carica il tuo questionario ESG</b> — analisi immediata con benchmark vs PMI italiane
    </div>
    """, unsafe_allow_html=True)

    template = """campo,valore
azienda,La Mia SRL
energia_rinnovabile,25
emissioni_co2,120
certificazione_iso14001,0
piano_riduzione_emissioni,0
rifiuti_differenziati,40
consumo_acqua,0
parita_genere,20
infortuni_zero,1
formazione_ore,15
welfare_aziendale,0
ccnl_applicato,1
supply_chain_etica,0
cda_indipendenti,30
revisione_esterna,1
piano_anticorruzione,0
politica_remunerazione,0
whistleblowing,0
rendicontazione_dnf,0
"""
    st.download_button("📥 Scarica template ESG (CSV)", template,
                      "template_esg.csv", "text/csv", use_container_width=True)

    uploaded = st.file_uploader("📂 Carica CSV questionario ESG",
                                type=["csv", "xlsx"], key="esg_upload")
    if uploaded:
        try:
            from pages_modules._file_import import read_financial_upload
            from utils.file_parser import _num
            data = read_financial_upload(uploaded)

            def g(k, default=0):
                return _num(data, k, default=default)

            azienda = str(data.get("azienda", "Azienda"))
            dati_e = {k: g(k, d) for (k, _, _, _, d, _) in DOMANDE_E}
            dati_s = {k: g(k, d) for (k, _, _, _, d, _) in DOMANDE_S}
            dati_g = {k: g(k, d) for (k, _, _, _, d, _) in DOMANDE_G}
            _esegui_analisi_esg(dati_e, dati_s, dati_g, azienda)
        except Exception as e:
            st.error(f"❌ Errore lettura file: {e}")


def _tab_manuale_esg():
    st.markdown("### 📝 Questionario ESG Interattivo")

    with st.form("esg_form"):
        azienda = st.text_input("🏢 Nome azienda", "La Mia SRL")

        st.markdown("---\n#### 🌍 Environmental (peso 35%)")
        col1, col2 = st.columns(2)
        dati_e = {}
        with col1:
            dati_e["energia_rinnovabile"] = st.slider("% energia rinnovabile", 0, 100, 20)
            dati_e["emissioni_co2"] = st.number_input("CO₂ (ton/M€ fatturato)", 0.0, 500.0, 120.0)
            dati_e["certificazione_iso14001"] = 1 if st.checkbox("ISO 14001 certificata") else 0
        with col2:
            dati_e["piano_riduzione_emissioni"] = 1 if st.checkbox("Piano riduzione emissioni") else 0
            dati_e["rifiuti_differenziati"] = st.slider("% rifiuti riciclati", 0, 100, 30)
            dati_e["consumo_acqua"] = 1 if st.checkbox("Sistemi risparmio acqua") else 0

        st.markdown("---\n#### 👥 Social (peso 35%)")
        col3, col4 = st.columns(2)
        dati_s = {}
        with col3:
            dati_s["parita_genere"] = st.slider("% donne in management", 0, 100, 20)
            dati_s["infortuni_zero"] = 1 if st.checkbox("Zero infortuni (ultimi 3 anni)") else 0
            dati_s["formazione_ore"] = st.number_input("Ore formazione/anno per dipendente", 0.0, 80.0, 10.0)
        with col4:
            dati_s["welfare_aziendale"] = 1 if st.checkbox("Piano welfare aziendale") else 0
            dati_s["ccnl_applicato"] = 1 if st.checkbox("CCNL applicato correttamente", value=True) else 0
            dati_s["supply_chain_etica"] = 1 if st.checkbox("Fornitori con codice etico") else 0

        st.markdown("---\n#### ⚖️ Governance (peso 30%)")
        col5, col6 = st.columns(2)
        dati_g = {}
        with col5:
            dati_g["cda_indipendenti"] = st.slider("% amministratori indipendenti", 0, 100, 20)
            dati_g["revisione_esterna"] = 1 if st.checkbox("Revisione esterna certificata") else 0
            dati_g["piano_anticorruzione"] = 1 if st.checkbox("Modello 231 attivo") else 0
        with col6:
            dati_g["politica_remunerazione"] = 1 if st.checkbox("Politica remunerazione trasparente") else 0
            dati_g["whistleblowing"] = 1 if st.checkbox("Sistema whistleblowing (D.Lgs. 24/2023)") else 0
            dati_g["rendicontazione_dnf"] = 1 if st.checkbox("Rendicontazione non finanziaria") else 0

        submitted = st.form_submit_button("🌿 Calcola ESG Score", use_container_width=True, type="primary")

    if submitted:
        _esegui_analisi_esg(dati_e, dati_s, dati_g, azienda, key_prefix="esg_manual_result")
