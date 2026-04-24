"""
Early Warning System — Codice della Crisi d'Impresa (D.Lgs. 14/2019)
DSCR monitoring a 12 mesi + alert automatici
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io


# ─── Costanti CCII ───────────────────────────────────────────────────────────
DSCR_SOGLIA_CRITICA = 1.0      # Sotto → rischio crisi CCII
DSCR_SOGLIA_ALLERTA = 1.1      # Zona di attenzione
DSCR_SOGLIA_SICURA  = 1.25     # Zona sicura
INDICI_CCII = {
    "DSCR": "Debt Service Coverage Ratio (≥1.0 obbligatorio per legge)",
    "Patrimonio netto / Totale debiti": "≥ 8% → allerta CCII",
    "Oneri finanziari / Ricavi": "≤ 3% → OK; >3% allerta",
    "EBITDA / Debito finanziario netto": "≥ 1.0 → sostenibile",
    "Liquidità corrente": "≥ 1.0 → equilibrio finanziario",
}


# ─── Calcoli DSCR ────────────────────────────────────────────────────────────
def calcola_dscr(ebitda: float, interessi: float, quota_capitale: float) -> float:
    """DSCR = EBITDA / (Interessi + Quote capitale)"""
    denominatore = interessi + quota_capitale
    if denominatore <= 0:
        return 99.0
    return round(ebitda / denominatore, 3)


def proiezione_dscr_12mesi(
    ebitda_attuale: float,
    interessi: float,
    quota_capitale: float,
    tasso_crescita_ebitda: float = 0.0,
    tasso_crescita_debito: float = 0.0
) -> pd.DataFrame:
    """Proietta DSCR mensile per 12 mesi."""
    mesi = []
    for i in range(1, 13):
        fattore_ebitda = (1 + tasso_crescita_ebitda / 100) ** (i / 12)
        fattore_debito = (1 + tasso_crescita_debito / 100) ** (i / 12)
        ebitda_m = ebitda_attuale / 12 * fattore_ebitda
        servizio_m = (interessi + quota_capitale) / 12 * fattore_debito
        dscr_m = ebitda_m / servizio_m if servizio_m > 0 else 99.0
        data_m = (datetime.now() + timedelta(days=30 * i)).strftime("%b %Y")
        mesi.append({
            "Mese": data_m,
            "EBITDA mensile": ebitda_m,
            "Servizio debito": servizio_m,
            "DSCR": round(dscr_m, 3),
            "Status": "🔴 Crisi" if dscr_m < DSCR_SOGLIA_CRITICA else (
                      "🟡 Allerta" if dscr_m < DSCR_SOGLIA_ALLERTA else (
                      "🟢 Sicuro" if dscr_m >= DSCR_SOGLIA_SICURA else "🔵 OK"))
        })
    return pd.DataFrame(mesi)


def calcola_indici_ccii(dati: dict) -> dict:
    """Calcola tutti gli indici di allerta CCII."""
    risultati = {}

    # DSCR
    dscr = calcola_dscr(
        dati.get("ebitda", 0),
        dati.get("interessi_passivi", 0),
        dati.get("quota_capitale", 0)
    )
    risultati["DSCR"] = {
        "valore": dscr,
        "soglia": DSCR_SOGLIA_CRITICA,
        "allerta": dscr < DSCR_SOGLIA_ALLERTA,
        "critico": dscr < DSCR_SOGLIA_CRITICA,
        "unita": "x",
        "descrizione": f"{'🔴 ALLERTA CCII' if dscr < 1.0 else '🟡 Attenzione' if dscr < 1.1 else '🟢 OK'}",
        "legge": "Art. 3 D.Lgs. 14/2019 — soglia legale ≥ 1.0"
    }

    # PN / Debiti totali
    pn = dati.get("patrimonio_netto", 0)
    debiti = dati.get("totale_debiti", 1)
    rapporto_pn = round(pn / debiti * 100, 2) if debiti > 0 else 0
    risultati["PN/Debiti"] = {
        "valore": rapporto_pn,
        "soglia": 8.0,
        "allerta": rapporto_pn < 8.0,
        "critico": pn < 0,
        "unita": "%",
        "descrizione": f"{'🔴 PN negativo' if pn < 0 else '🟡 Sotto soglia' if rapporto_pn < 8 else '🟢 OK'}",
        "legge": "Indice di adeguatezza patrimoniale — soglia 8%"
    }

    # Oneri finanziari / Ricavi
    oneri = dati.get("interessi_passivi", 0)
    ricavi = dati.get("ricavi_netti", 1)
    rapporto_oneri = round(oneri / ricavi * 100, 2) if ricavi > 0 else 0
    risultati["Oneri/Ricavi"] = {
        "valore": rapporto_oneri,
        "soglia": 3.0,
        "allerta": rapporto_oneri > 3.0,
        "critico": rapporto_oneri > 8.0,
        "unita": "%",
        "descrizione": f"{'🔴 Critico' if rapporto_oneri > 8 else '🟡 Attenzione' if rapporto_oneri > 3 else '🟢 OK'}",
        "legge": "Sostenibilità oneri finanziari — soglia 3%"
    }

    # EBITDA / Debito finanziario netto
    debito_fin = dati.get("debito_finanziario_netto", debiti * 0.6)
    ebitda = dati.get("ebitda", 0)
    lev = round(ebitda / debito_fin, 2) if debito_fin > 0 else 0
    risultati["EBITDA/Debito_fin"] = {
        "valore": lev,
        "soglia": 1.0,
        "allerta": lev < 1.0,
        "critico": lev < 0,
        "unita": "x",
        "descrizione": f"{'🔴 Insostenibile' if lev < 0 else '🟡 Sotto soglia' if lev < 1 else '🟢 OK'}",
        "legge": "Leva finanziaria — soglia ≥ 1.0x"
    }

    # Liquidità corrente
    att_corr = dati.get("attivo_corrente", dati.get("liquidita", 0) * 3)
    pass_corr = dati.get("passivo_corrente", debiti * 0.4)
    liq_corr = round(att_corr / pass_corr, 2) if pass_corr > 0 else 0
    risultati["Liquidita_corrente"] = {
        "valore": liq_corr,
        "soglia": 1.0,
        "allerta": liq_corr < 1.0,
        "critico": liq_corr < 0.5,
        "unita": "x",
        "descrizione": f"{'🔴 Crisi liquidità' if liq_corr < 0.5 else '🟡 Attenzione' if liq_corr < 1 else '🟢 OK'}",
        "legge": "Equilibrio finanziario corrente — soglia ≥ 1.0"
    }

    return risultati


def genera_narrative_allerta(indici: dict, dscr_df: pd.DataFrame) -> list:
    """Genera messaggi di allerta legali con azioni correttive."""
    allerte = []

    if indici["DSCR"]["critico"]:
        allerte.append({
            "livello": "🚨 CRITICO — Obbligo CCII",
            "messaggio": f"DSCR = {indici['DSCR']['valore']}x — SOTTO LA SOGLIA LEGALE (1.0x). "
                        "L'organo di controllo DEVE segnalare la crisi. "
                        "Obbligo di adottare misure entro 30 giorni.",
            "azione": "Convocare CDA straordinario + piano di risanamento ex art. 56 CCII"
        })

    if indici["PN/Debiti"]["critico"]:
        allerte.append({
            "livello": "🚨 CRITICO — Patrimonio Netto negativo",
            "messaggio": "Patrimonio netto negativo: la società opera in stato di perdita "
                        "del capitale. Obbligo di copertura perdite (art. 2447 c.c.).",
            "azione": "Ricapitalizzazione o liquidazione entro 90 giorni"
        })

    mesi_critici = dscr_df[dscr_df["DSCR"] < DSCR_SOGLIA_CRITICA]
    if len(mesi_critici) > 0:
        primo_mese = mesi_critici.iloc[0]["Mese"]
        allerte.append({
            "livello": "⚠️ ALLERTA PREVISIONALE",
            "messaggio": f"Proiezione: DSCR scenderà sotto 1.0 a partire da {primo_mese}. "
                        f"Coinvolti {len(mesi_critici)} mesi nei prossimi 12.",
            "azione": "Rinegoziare scadenze debito o incrementare EBITDA prima di tale data"
        })

    if indici["Oneri/Ricavi"]["critico"]:
        allerte.append({
            "livello": "⚠️ ALLERTA — Oneri finanziari eccessivi",
            "messaggio": f"Oneri finanziari/Ricavi = {indici['Oneri/Ricavi']['valore']}% "
                        "(soglia CCII: 3%). Il costo del debito erode i margini.",
            "azione": "Rinegoziare tassi o estinguere anticipatamente i debiti più costosi"
        })

    if not allerte:
        allerte.append({
            "livello": "✅ NESSUNA ALLERTA CCII",
            "messaggio": "Tutti gli indici di allerta sono nei range di sicurezza. "
                        "L'azienda non è soggetta a obblighi di segnalazione.",
            "azione": "Continuare monitoraggio trimestrale"
        })

    return allerte


# ─── Grafici ─────────────────────────────────────────────────────────────────
def grafico_dscr_proiezione(df: pd.DataFrame) -> go.Figure:
    colori = ["#ef4444" if d < 1.0 else "#f59e0b" if d < 1.1 else "#22c55e"
              for d in df["DSCR"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Mese"], y=df["DSCR"],
        marker_color=colori,
        name="DSCR mensile",
        text=[f"{d:.2f}" for d in df["DSCR"]],
        textposition="outside"
    ))
    fig.add_hline(y=DSCR_SOGLIA_CRITICA, line_dash="dash", line_color="#ef4444",
                  annotation_text="⚠️ Soglia CCII (1.0)")
    fig.add_hline(y=DSCR_SOGLIA_ALLERTA, line_dash="dot", line_color="#f59e0b",
                  annotation_text="Attenzione (1.1)")
    fig.add_hline(y=DSCR_SOGLIA_SICURA, line_dash="dot", line_color="#22c55e",
                  annotation_text="Sicuro (1.25)")
    fig.update_layout(
        title="📈 Proiezione DSCR 12 mesi — Codice della Crisi d'Impresa",
        xaxis_title="Mese",
        yaxis_title="DSCR",
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        showlegend=False
    )
    return fig


def grafico_radar_indici(indici: dict) -> go.Figure:
    labels = ["DSCR", "PN/Debiti\n(norm)", "Oneri/Ricavi\n(inv)", "EBITDA/Fin", "Liquidità"]
    dscr_norm = min(indici["DSCR"]["valore"] / 2.0, 1.0)
    pn_norm   = min(max(indici["PN/Debiti"]["valore"] / 20.0, 0), 1.0)
    oneri_inv = max(1.0 - indici["Oneri/Ricavi"]["valore"] / 10.0, 0)
    ebitda_n  = min(max(indici["EBITDA/Debito_fin"]["valore"] / 2.0, 0), 1.0)
    liq_norm  = min(indici["Liquidita_corrente"]["valore"] / 2.0, 1.0)
    values = [dscr_norm, pn_norm, oneri_inv, ebitda_n, liq_norm]
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(99,102,241,0.25)",
        line=dict(color="#6366f1", width=2),
        name="Indici CCII"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="🕸️ Radar Indici di Allerta CCII",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        showlegend=False
    )
    return fig


# ─── Parse CSV per Early Warning ─────────────────────────────────────────────
def parse_csv_early_warning(uploaded_file) -> dict:
    try:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        uploaded_file.seek(0)
        lines = [l for l in content.splitlines() if not l.strip().startswith("#") and l.strip()]
        df = pd.read_csv(io.StringIO("\n".join(lines)), header=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if "campo" in df.columns and ("valore" in df.columns or df.columns[1]):
            val_col = "valore" if "valore" in df.columns else df.columns[1]
            data = {str(r["campo"]).strip().lower(): r[val_col] for _, r in df.iterrows()
                    if pd.notna(r[val_col])}
        else:
            return None

        def g(keys, default=0.0):
            for k in keys:
                if k in data:
                    try:
                        return float(str(data[k]).replace(".", "").replace(",", ".").strip())
                    except:
                        pass
            return default

        return {
            "azienda": str(data.get("azienda", data.get("nome_azienda", "Azienda"))),
            "ebitda": g(["ebitda", "margine_operativo_lordo"]),
            "interessi_passivi": g(["interessi_passivi", "oneri_finanziari", "of"]),
            "quota_capitale": g(["quota_capitale", "rimborso_debiti", "rata_capitale"]),
            "patrimonio_netto": g(["patrimonio_netto", "equity"]),
            "totale_debiti": g(["totale_debiti", "debiti_totali", "passivo_totale"]),
            "ricavi_netti": g(["ricavi_netti", "fatturato", "ricavi_vendite"]),
            "liquidita": g(["liquidita", "disponibilita_liquide", "cassa"]),
            "attivo_corrente": g(["attivo_corrente", "capitale_circolante"]),
            "passivo_corrente": g(["passivo_corrente", "debiti_breve_termine"]),
            "debito_finanziario_netto": g(["debito_finanziario_netto", "pfn", "posizione_finanziaria_netta"]),
        }
    except Exception as e:
        st.error(f"Errore parsing: {e}")
        return None


# ─── UI Principale ────────────────────────────────────────────────────────────
def show_early_warning():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #dc2626, #991b1b);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.8rem;'>
            🚨 Early Warning System
        </h2>
        <p style='color: rgba(255,255,255,0.85); margin: 0.3rem 0 0;'>
            Codice della Crisi d'Impresa — D.Lgs. 14/2019 | DSCR monitoring a 12 mesi
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Info normativa
    with st.expander("ℹ️ Cos'è il DSCR e perché è obbligatorio?", expanded=False):
        st.markdown("""
        **D.Lgs. 14/2019 — Codice della Crisi d'Impresa e dell'Insolvenza (CCII)**

        Dal 15 luglio 2022, le imprese italiane sono obbligate ad adottare **"assetti organizzativi, 
        amministrativi e contabili"** per rilevare tempestivamente lo stato di crisi.

        L'indicatore principale previsto dall'art. 3 CCII è il **DSCR (Debt Service Coverage Ratio)**:

        > **DSCR = EBITDA prospettico / Servizio del debito (interessi + quota capitale)**

        - **DSCR < 1.0** → L'azienda NON genera abbastanza cash per pagare i debiti → **obbligo di segnalazione**
        - **DSCR 1.0–1.1** → Zona di attenzione → monitoraggio intensificato
        - **DSCR ≥ 1.25** → Zona sicura

        L'organo di controllo (sindaco/revisore) che non segnala la crisi rischia **responsabilità civile e penale**.
        """)

    tab_upload, tab_manuale = st.tabs(["⚡ Carica & Analizza", "📝 Inserisci Manualmente"])

    with tab_upload:
        _tab_upload_early_warning()

    with tab_manuale:
        _tab_manuale_early_warning()


def _esegui_analisi_early_warning(dati: dict, crescita_ebitda: float = 0.0, crescita_debito: float = 0.0):
    """Esegue e mostra l'analisi completa Early Warning."""
    azienda = dati.get("azienda", "Azienda")

    indici = calcola_indici_ccii(dati)
    dscr_df = proiezione_dscr_12mesi(
        dati.get("ebitda", 0),
        dati.get("interessi_passivi", 0),
        dati.get("quota_capitale", 0),
        crescita_ebitda,
        crescita_debito
    )
    allerte = genera_narrative_allerta(indici, dscr_df)
    n_critici = sum(1 for i in indici.values() if i["critico"])
    n_allerta  = sum(1 for i in indici.values() if i["allerta"] and not i["critico"])

    # Header risultati
    st.markdown(f"---\n### 📊 Risultati Early Warning — **{azienda}**")

    # KPI indici
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        dscr_val = indici["DSCR"]["valore"]
        st.metric("DSCR attuale", f"{dscr_val:.2f}x",
                  delta=f"{'🔴 CRISI' if dscr_val < 1.0 else '🟡 Allerta' if dscr_val < 1.1 else '🟢 OK'}")
    with col2:
        st.metric("Indici critici", f"{n_critici}/5",
                  delta="Azione richiesta" if n_critici > 0 else "Tutto OK",
                  delta_color="inverse")
    with col3:
        st.metric("Indici in allerta", f"{n_allerta}/5")
    with col4:
        mesi_crisi = len(dscr_df[dscr_df["DSCR"] < 1.0])
        st.metric("Mesi in crisi (12m)", f"{mesi_crisi}",
                  delta="⚠️ Azione urgente" if mesi_crisi > 0 else "Nessuno",
                  delta_color="inverse")

    # Allerte
    st.markdown("### ⚖️ Allerte CCII")
    for allerta in allerte:
        if "CRITICO" in allerta["livello"]:
            st.error(f"**{allerta['livello']}**\n\n{allerta['messaggio']}\n\n💡 **Azione**: {allerta['azione']}")
        elif "ALLERTA" in allerta["livello"]:
            st.warning(f"**{allerta['livello']}**\n\n{allerta['messaggio']}\n\n💡 **Azione**: {allerta['azione']}")
        else:
            st.success(f"**{allerta['livello']}**\n\n{allerta['messaggio']}\n\n✅ {allerta['azione']}")

    # Grafici
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.plotly_chart(grafico_dscr_proiezione(dscr_df), use_container_width=True)
    with col_g2:
        st.plotly_chart(grafico_radar_indici(indici), use_container_width=True)

    # Tabella DSCR mensile — usa .map() invece di .applymap() (deprecato in pandas >= 2.1)
    with st.expander("📋 Dettaglio DSCR mese per mese"):
        st.dataframe(
            dscr_df[["Mese", "DSCR", "Status"]].style.map(
                lambda v: "color: #ef4444" if isinstance(v, str) and "Crisi" in v
                else "color: #f59e0b" if isinstance(v, str) and "Allerta" in v
                else "color: #22c55e" if isinstance(v, str) and "Sicuro" in v else "",
                subset=["Status"]
            ),
            use_container_width=True, hide_index=True
        )

    # Tabella tutti gli indici
    st.markdown("### 📐 Tutti gli Indici di Allerta CCII")
    rows = []
    for nome, ind in indici.items():
        rows.append({
            "Indice": nome.replace("_", " "),
            "Valore": f"{ind['valore']}{ind['unita']}",
            "Status": ind["descrizione"],
            "Riferimento normativo": ind["legge"]
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Export
    st.markdown("---")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        csv_out = dscr_df.to_csv(index=False)
        st.download_button("📥 Scarica proiezione DSCR (CSV)", csv_out,
                          f"DSCR_{azienda.replace(' ','_')}.csv", "text/csv",
                          use_container_width=True)
    with col_e2:
        st.info("📄 Report PDF CCII completo disponibile dalla sezione Audit Report ISA 320")


def _tab_upload_early_warning():
    st.markdown("""
    <div style='background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.3);
                border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
        <b>⚡ Carica il bilancio</b> — il sistema analizza automaticamente DSCR e tutti 
        gli indici di allerta CCII obbligatori per legge.
    </div>
    """, unsafe_allow_html=True)

    # Template
    template_csv = """campo,valore,descrizione
azienda,La Mia SRL,Nome azienda
ebitda,500000,EBITDA annuo
interessi_passivi,80000,Oneri finanziari annui
quota_capitale,120000,Quota annua rimborso debiti
patrimonio_netto,800000,Patrimonio netto
totale_debiti,2000000,Totale debiti
ricavi_netti,3000000,Fatturato
liquidita,150000,Disponibilità liquide
attivo_corrente,600000,Attivo corrente
passivo_corrente,500000,Passivo corrente
debito_finanziario_netto,1500000,PFN (Posizione Finanziaria Netta)
"""
    st.download_button("📥 Scarica template CSV", template_csv,
                      "template_early_warning.csv", "text/csv",
                      use_container_width=True)

    uploaded = st.file_uploader("📂 Carica CSV o Excel bilancio",
                                type=["csv", "xlsx", "xls"],
                                key="ew_upload")

    # Parametri scenari
    with st.expander("⚙️ Parametri proiezione (opzionali)"):
        col1, col2 = st.columns(2)
        with col1:
            crescita_ebitda = st.slider("Crescita EBITDA annua %", -20, 30, 0,
                                        help="Stima variazione EBITDA nei 12 mesi")
        with col2:
            crescita_debito = st.slider("Crescita servizio debito %", -10, 20, 0,
                                        help="Stima variazione rata debito")

    if uploaded:
        dati = parse_csv_early_warning(uploaded)
        if dati:
            _esegui_analisi_early_warning(dati, crescita_ebitda, crescita_debito)
        else:
            st.error("❌ File non riconosciuto. Usa il template CSV scaricabile.")


def _tab_manuale_early_warning():
    st.markdown("### 📝 Inserisci i dati manualmente")

    with st.form("ew_form"):
        col1, col2 = st.columns(2)
        with col1:
            azienda = st.text_input("🏢 Nome azienda", "La Mia SRL")
            ebitda = st.number_input("EBITDA annuo (€)", value=500000.0, step=10000.0)
            interessi = st.number_input("Interessi passivi annui (€)", value=80000.0, step=1000.0, min_value=0.0)
            quota_cap = st.number_input("Quota capitale annua (€)", value=120000.0, step=1000.0, min_value=0.0)
            ricavi = st.number_input("Ricavi netti (€)", value=3000000.0, step=50000.0)
        with col2:
            pn = st.number_input("Patrimonio netto (€)", value=800000.0, step=10000.0)
            debiti = st.number_input("Totale debiti (€)", value=2000000.0, step=50000.0)
            liq = st.number_input("Liquidità disponibile (€)", value=150000.0, step=10000.0, min_value=0.0)
            att_corr = st.number_input("Attivo corrente (€)", value=600000.0, step=10000.0)
            pass_corr = st.number_input("Passivo corrente (€)", value=500000.0, step=10000.0)

        st.markdown("**📈 Proiezione 12 mesi**")
        col3, col4 = st.columns(2)
        with col3:
            crescita_ebitda = st.slider("Crescita EBITDA attesa %", -20, 30, 0)
        with col4:
            crescita_debito = st.slider("Crescita debito attesa %", -10, 20, 0)

        submitted = st.form_submit_button("🚨 Calcola Early Warning", use_container_width=True,
                                          type="primary")

    if submitted:
        dati = {
            "azienda": azienda,
            "ebitda": ebitda,
            "interessi_passivi": interessi,
            "quota_capitale": quota_cap,
            "patrimonio_netto": pn,
            "totale_debiti": debiti,
            "ricavi_netti": ricavi,
            "liquidita": liq,
            "attivo_corrente": att_corr,
            "passivo_corrente": pass_corr,
            "debito_finanziario_netto": debiti * 0.6,
        }
        _esegui_analisi_early_warning(dati, crescita_ebitda, crescita_debito)
