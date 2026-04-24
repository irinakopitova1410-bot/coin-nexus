"""
Open Banking PSD2/PSD3 — Collegamento banca real-time
Integrazione con aggregatori: Fabrick, Salt Edge, Nordigen (GoCardless)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import io


# ─── Dati demo realistici ────────────────────────────────────────────────────
def genera_movimenti_demo(saldo_iniziale: float = 50000, giorni: int = 90) -> pd.DataFrame:
    """Genera movimenti bancari realistici per demo."""
    random.seed(42)
    movimenti = []
    saldo = saldo_iniziale
    data_base = datetime.now() - timedelta(days=giorni)

    descrizioni_entrate = [
        "Bonifico cliente ALFA SRL", "Accredito fattura #1234",
        "Pagamento cliente BETA SpA", "Incasso RiBa cliente",
        "Bonifico GAMMA SRL fat. #567", "Accredito anticipo fatture",
    ]
    descrizioni_uscite = [
        "Bonifico fornitore DELTA SRL", "Pagamento F24 IVA",
        "Rata mutuo immobile", "Stipendi dipendenti",
        "Pagamento leasing macchinari", "Utenze e servizi",
        "Pagamento fornitore ZETA SpA", "Assicurazioni aziendali",
    ]

    for i in range(giorni):
        data = data_base + timedelta(days=i)
        if data.weekday() < 5:  # Solo giorni lavorativi
            # 1-2 movimenti al giorno
            n_mov = random.randint(0, 2)
            for _ in range(n_mov):
                if random.random() > 0.45:  # 55% entrate
                    importo = random.uniform(5000, 80000)
                    desc = random.choice(descrizioni_entrate)
                    tipo = "CREDIT"
                else:
                    importo = -random.uniform(2000, 50000)
                    desc = random.choice(descrizioni_uscite)
                    tipo = "DEBIT"
                saldo += importo
                movimenti.append({
                    "data": data.strftime("%Y-%m-%d"),
                    "descrizione": desc,
                    "importo": round(importo, 2),
                    "tipo": tipo,
                    "saldo": round(saldo, 2)
                })

    return pd.DataFrame(movimenti).sort_values("data", ascending=False)


def analisi_flussi(df: pd.DataFrame) -> dict:
    """Analizza i flussi bancari per previsione e alerting."""
    entrate = df[df["importo"] > 0]["importo"].sum()
    uscite = abs(df[df["importo"] < 0]["importo"].sum())
    saldo_attuale = df.iloc[0]["saldo"] if len(df) > 0 else 0
    flusso_netto = entrate - uscite
    giorni = (pd.to_datetime(df["data"].max()) - pd.to_datetime(df["data"].min())).days + 1
    burn_rate_giornaliero = uscite / giorni if giorni > 0 else 0
    giorni_autonomia = saldo_attuale / burn_rate_giornaliero if burn_rate_giornaliero > 0 else 999

    return {
        "saldo_attuale": saldo_attuale,
        "entrate_periodo": entrate,
        "uscite_periodo": uscite,
        "flusso_netto": flusso_netto,
        "burn_rate_giornaliero": burn_rate_giornaliero,
        "giorni_autonomia": giorni_autonomia,
        "n_movimenti": len(df),
        "dscr_proxy": entrate / uscite if uscite > 0 else 99,
    }


def previsione_saldo_30gg(saldo: float, entrate_medie: float, uscite_medie: float) -> pd.DataFrame:
    """Previsione saldo a 30 giorni basata su trend storico."""
    giorni_prev = []
    saldo_prev = saldo
    data_oggi = datetime.now()
    for i in range(1, 31):
        data = data_oggi + timedelta(days=i)
        if data.weekday() < 5:
            variazione = (entrate_medie - uscite_medie) / 22  # ~22 giorni lavorativi/mese
            rumore = variazione * 0.3 * (random.random() - 0.5)
            saldo_prev += variazione + rumore
        giorni_prev.append({
            "data": data.strftime("%d/%m"),
            "saldo_previsto": round(saldo_prev, 0),
            "alert": saldo_prev < 10000
        })
    return pd.DataFrame(giorni_prev)


# ─── Grafici ─────────────────────────────────────────────────────────────────
def grafico_saldo_storico(df: pd.DataFrame) -> go.Figure:
    df_plot = df.copy()
    df_plot["data"] = pd.to_datetime(df_plot["data"])
    df_plot = df_plot.sort_values("data")
    df_plot["colore"] = df_plot["saldo"].apply(
        lambda x: "#ef4444" if x < 10000 else "#f59e0b" if x < 30000 else "#22c55e")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["data"], y=df_plot["saldo"],
        mode="lines+markers",
        line=dict(color="#6366f1", width=2),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.1)",
        name="Saldo"
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color="#ef4444",
                  annotation_text="⚠️ Soglia critica")
    fig.update_layout(
        title="💳 Andamento saldo bancario",
        xaxis_title="Data", yaxis_title="Saldo (€)",
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )
    return fig


def grafico_previsione(df_prev: pd.DataFrame) -> go.Figure:
    colori = ["#ef4444" if a else "#22c55e" for a in df_prev["alert"]]
    fig = go.Figure(go.Bar(
        x=df_prev["data"],
        y=df_prev["saldo_previsto"],
        marker_color=colori,
        name="Saldo previsto"
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color="#ef4444",
                  annotation_text="⚠️ Soglia minima")
    fig.update_layout(
        title="🔮 Previsione saldo 30 giorni",
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )
    return fig


def grafico_entrate_uscite(df: pd.DataFrame) -> go.Figure:
    df["data_mese"] = pd.to_datetime(df["data"]).dt.strftime("%b %Y")
    mensile = df.groupby(["data_mese", "tipo"])["importo"].sum().abs().reset_index()
    entrate_m = mensile[mensile["tipo"] == "CREDIT"].set_index("data_mese")["importo"]
    uscite_m  = mensile[mensile["tipo"] == "DEBIT"].set_index("data_mese")["importo"]
    mesi = sorted(set(entrate_m.index) | set(uscite_m.index))

    fig = go.Figure(data=[
        go.Bar(name="📥 Entrate", x=mesi, y=[entrate_m.get(m, 0) for m in mesi],
               marker_color="#22c55e"),
        go.Bar(name="📤 Uscite",  x=mesi, y=[uscite_m.get(m, 0) for m in mesi],
               marker_color="#ef4444"),
    ])
    fig.update_layout(barmode="group", title="📊 Entrate vs Uscite per mese",
                      height=320, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"))
    return fig


# ─── UI ──────────────────────────────────────────────────────────────────────
def show_open_banking():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0f172a, #1e3a5f);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
                border: 1px solid #2563eb;'>
        <h2 style='color:white; margin:0; font-size:1.8rem;'>🏦 Open Banking</h2>
        <p style='color: rgba(255,255,255,0.85); margin: 0.3rem 0 0;'>
            PSD2/PSD3 · Saldi reali · Previsione sconfinamento · Alert automatici
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_connetti, tab_demo, tab_upload = st.tabs([
        "🔌 Collega la tua Banca", "🎯 Demo Live", "📂 Carica Estratto Conto"
    ])

    with tab_connetti:
        _tab_connetti_banca()
    with tab_demo:
        _tab_demo_open_banking()
    with tab_upload:
        _tab_upload_estratto()


def _tab_connetti_banca():
    st.markdown("### 🔌 Collegamento Open Banking (PSD2/PSD3)")

    st.markdown("""
    <div style='background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.3);
                border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem;'>
        <b>Come funziona:</b><br>
        1. Seleziona la tua banca dalla lista<br>
        2. Autenticati in modo sicuro tramite il portale della tua banca<br>
        3. Nexus scarica i movimenti degli ultimi 90 giorni ogni mattina<br>
        4. Ricevi alert automatici se il saldo scende sotto la soglia<br>
        <br>
        🔒 <b>Sicurezza</b>: Nexus non vede mai le tue credenziali bancarie — 
        usa solo token PSD2 con accesso read-only.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🇮🇹 Banche italiane supportate")
        banche = [
            "🏛️ Intesa Sanpaolo", "🏦 UniCredit", "🏦 Banco BPM",
            "🏦 Monte dei Paschi di Siena", "🏦 BPER Banca",
            "🏦 Mediobanca", "🏦 Credito Emiliano (Credem)",
            "🏦 Banca Mediolanum", "🏦 Fineco Bank", "🏦 ING Italia",
            "🏦 N26 Italia", "🏦 Revolut Business",
        ]
        for b in banche:
            st.markdown(f"- {b}")

    with col2:
        st.markdown("#### ⚙️ Configura il collegamento")
        banca_sel = st.selectbox("Seleziona la tua banca", [b.split(" ", 1)[1] for b in banche])
        iban = st.text_input("IBAN conto corrente aziendale", placeholder="IT60 X054 2811 1010 0000 0123 456")
        soglia_alert = st.number_input("Soglia alert saldo minimo (€)", value=15000.0, step=1000.0)

        if st.button("🔌 Avvia collegamento PSD2", type="primary", use_container_width=True):
            with st.spinner(f"Connessione a {banca_sel} in corso..."):
                import time; time.sleep(1.5)
            st.info(f"""
            **🚧 Integrazione PSD2 in fase di sviluppo**
            
            Per attivare il collegamento live con **{banca_sel}**:
            
            1. Configura API key **Salt Edge** o **Fabrick** nei secrets dell'app
            2. Il redirect OAuth bancario verrà gestito automaticamente
            3. I movimenti saranno disponibili entro 30 secondi
            
            👉 Nel frattempo, usa la tab **Demo Live** per vedere l'esperienza completa.
            
            📧 Contatta Nexus per attivare il modulo banking: [irina@nexusfinance.it](mailto:irina.kopitova1410@gmail.com)
            """)

    # Alert configuration
    st.markdown("---\n#### 🔔 Configura Alert Automatici")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.toggle("📧 Alert email saldo basso", value=True)
        st.toggle("📉 Alert DSCR sotto soglia", value=True)
    with col_a2:
        st.toggle("💳 Alert pagamento in scadenza", value=False)
        st.toggle("📊 Report settimanale flussi", value=True)
    with col_a3:
        st.toggle("🚨 Alert sconfinamento previsto", value=True)
        st.toggle("📱 Notifiche WhatsApp Business", value=False,
                 help="Disponibile con piano Premium")


def _tab_demo_open_banking():
    st.markdown("### 🎯 Demo — Conto Corrente Aziendale Live")
    st.info("Dati simulati realistici — così funzionerà con il tuo vero conto corrente.")

    azienda = st.text_input("Nome azienda (demo)", "La Mia SRL")
    saldo_demo = st.number_input("Saldo iniziale demo (€)", value=65000.0, step=5000.0)

    df_mov = genera_movimenti_demo(saldo_demo, giorni=90)
    analisi = analisi_flussi(df_mov)

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        color = "#22c55e" if analisi["saldo_attuale"] > 30000 else "#f59e0b" if analisi["saldo_attuale"] > 10000 else "#ef4444"
        st.metric("💳 Saldo attuale", f"€{analisi['saldo_attuale']:,.0f}")
    with col2:
        st.metric("📥 Entrate (90gg)", f"€{analisi['entrate_periodo']:,.0f}")
    with col3:
        st.metric("📤 Uscite (90gg)", f"€{analisi['uscite_periodo']:,.0f}")
    with col4:
        giorni = analisi["giorni_autonomia"]
        delta_col = "normal" if giorni > 45 else "inverse"
        st.metric("⏳ Autonomia stimata",
                  f"{int(giorni)} giorni" if giorni < 500 else "∞",
                  delta=f"{'🟢 OK' if giorni > 60 else '🟡 Attenzione' if giorni > 30 else '🔴 Critico'}",
                  delta_color=delta_col)

    # Alert sconfinamento
    if analisi["giorni_autonomia"] < 30:
        st.error(f"🚨 **ALERT**: Saldo esaurito in {int(analisi['giorni_autonomia'])} giorni! "
                "Azione immediata necessaria.")
    elif analisi["giorni_autonomia"] < 60:
        st.warning(f"⚠️ **Attenzione**: Autonomia finanziaria di soli {int(analisi['giorni_autonomia'])} giorni. "
                  "Considerare linea di credito o anticipo fatture.")

    # Grafici
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(grafico_saldo_storico(df_mov), use_container_width=True)
    with col_g2:
        df_prev = previsione_saldo_30gg(
            analisi["saldo_attuale"],
            analisi["entrate_periodo"] / 3,
            analisi["uscite_periodo"] / 3
        )
        st.plotly_chart(grafico_previsione(df_prev), use_container_width=True)

    st.plotly_chart(grafico_entrate_uscite(df_mov), use_container_width=True)

    # Movimenti recenti
    st.markdown("### 📋 Ultimi movimenti")
    df_display = df_mov.head(20).copy()
    df_display["importo_fmt"] = df_display["importo"].apply(
        lambda x: f"🟢 +€{x:,.0f}" if x > 0 else f"🔴 -€{abs(x):,.0f}")
    df_display["saldo_fmt"] = df_display["saldo"].apply(lambda x: f"€{x:,.0f}")
    st.dataframe(
        df_display[["data", "descrizione", "importo_fmt", "saldo_fmt"]].rename(columns={
            "data": "Data", "descrizione": "Descrizione",
            "importo_fmt": "Importo", "saldo_fmt": "Saldo"
        }),
        use_container_width=True, hide_index=True
    )

    csv_out = df_mov.to_csv(index=False)
    st.download_button("📥 Scarica movimenti (CSV)", csv_out,
                      f"Movimenti_{azienda}.csv", "text/csv",
                      use_container_width=True)


def _tab_upload_estratto():
    st.markdown("### 📂 Carica Estratto Conto")
    st.markdown("Carica il CSV dell'estratto conto bancario — Nexus analizza i flussi automaticamente.")

    template = """data,descrizione,importo,tipo
2024-03-01,Bonifico cliente ALFA SRL,25000.00,CREDIT
2024-03-02,Pagamento fornitore BETA SRL,-12000.00,DEBIT
2024-03-03,Stipendi dipendenti,-45000.00,DEBIT
2024-03-05,Accredito fattura #1234,38000.00,CREDIT
2024-03-08,F24 IVA,-8500.00,DEBIT
2024-03-10,Incasso RiBa clienti,22000.00,CREDIT
"""
    st.download_button("📥 Template estratto conto (CSV)", template,
                      "template_estratto_conto.csv", "text/csv", use_container_width=True)

    uploaded = st.file_uploader("📂 Carica estratto conto CSV",
                                type=["csv", "xlsx"], key="banking_upload")
    if uploaded:
        try:
            content = uploaded.read().decode("utf-8", errors="replace")
            uploaded.seek(0)
            lines = [l for l in content.splitlines() if not l.strip().startswith("#") and l.strip()]
            df = pd.read_csv(io.StringIO("\n".join(lines)))
            df.columns = [str(c).strip().lower() for c in df.columns]

            if "importo" not in df.columns:
                st.error("❌ Il CSV deve avere una colonna 'importo'")
                return

            df["importo"] = pd.to_numeric(df["importo"], errors="coerce").fillna(0)
            if "tipo" not in df.columns:
                df["tipo"] = df["importo"].apply(lambda x: "CREDIT" if x > 0 else "DEBIT")
            if "saldo" not in df.columns:
                df["saldo"] = df["importo"].cumsum()
            if "data" not in df.columns:
                df["data"] = pd.date_range(end=datetime.now(), periods=len(df)).strftime("%Y-%m-%d")

            analisi = analisi_flussi(df)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📥 Entrate totali", f"€{analisi['entrate_periodo']:,.0f}")
            with col2:
                st.metric("📤 Uscite totali", f"€{analisi['uscite_periodo']:,.0f}")
            with col3:
                st.metric("💰 Flusso netto", f"€{analisi['flusso_netto']:,.0f}")

            st.plotly_chart(grafico_saldo_storico(df), use_container_width=True)
            st.dataframe(df.head(30), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"❌ Errore lettura file: {e}")
