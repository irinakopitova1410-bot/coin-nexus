"""
NEXUS Finance Pro — Credit Readiness Dashboard
La schermata più importante: porta l'azienda da NON finanziabile → FINANZIABILE
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
from engine.credit_readiness import analyze_credit_readiness, CreditReadinessResult


# ─── Helpers UI ──────────────────────────────────────────────────────────────

def fmt_eur(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"€{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"€{value/1_000:.0f}K"
    else:
        return f"€{value:.0f}"


def gauge_chart(score: float, rating: str) -> go.Figure:
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"Credit Score — {rating}", "font": {"size": 18, "color": "#1e293b"}},
        number={"font": {"size": 48, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748b"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30],  "color": "#fee2e2"},
                {"range": [30, 50], "color": "#fef3c7"},
                {"range": [50, 70], "color": "#fef9c3"},
                {"range": [70, 85], "color": "#dcfce7"},
                {"range": [85, 100],"color": "#bbf7d0"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )
    return fig


def credit_bar_chart(oggi: float, potenziale: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Oggi", "Potenziale"],
        y=[oggi, potenziale],
        marker_color=["#3b82f6", "#22c55e"],
        text=[fmt_eur(oggi), fmt_eur(potenziale)],
        textposition="outside",
        textfont={"size": 14, "color": "#1e293b"},
        width=0.4,
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"showgrid": True, "gridcolor": "#f1f5f9", "tickformat": "€,.0f"},
        xaxis={"showgrid": False},
        showlegend=False,
        font={"family": "Inter, sans-serif"},
    )
    return fig


def score_breakdown_chart(breakdown: dict) -> go.Figure:
    categories = list(breakdown.keys())
    values = list(breakdown.values())
    maxima = {
        "EBITDA Margin": 25, "Debt / EBITDA": 20, "Liquidità Corrente": 20,
        "Cash Flow Operativo": 15, "Solidità Patrimoniale": 12, "Trend Ricavi": 8,
    }
    normalized = [(v / maxima.get(c, 20)) * 100 for c, v in zip(categories, values)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=normalized + [normalized[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(59,130,246,0.15)",
        line=dict(color="#3b82f6", width=2),
        name="Score attuale",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%"),
            angularaxis=dict(tickfont={"size": 11}),
        ),
        height=280,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font={"family": "Inter, sans-serif"},
    )
    return fig


# ─── Parser file CSV/Excel ────────────────────────────────────────────────────

FIELD_MAP = {
    # fatturato
    "fatturato": "fatturato",
    "ricavi": "fatturato",
    "revenue": "fatturato",
    "ricavi_netti": "fatturato",
    # ebitda
    "ebitda": "ebitda",
    # ebit
    "ebit": "ebit",
    "reddito_operativo": "ebit",
    # utile netto
    "utile_netto": "utile_netto",
    "net_income": "utile_netto",
    "risultato_netto": "utile_netto",
    # fatturato precedente
    "fatturato_prev": "fatturato_prev",
    "fatturato_precedente": "fatturato_prev",
    "ricavi_anno_precedente": "fatturato_prev",
    # attivo corrente
    "attivo_corrente": "attivo_corrente",
    "current_assets": "attivo_corrente",
    # passivo corrente
    "passivo_corrente": "passivo_corrente",
    "current_liabilities": "passivo_corrente",
    # debiti finanziari
    "debiti_finanziari": "debiti_finanziari",
    "total_debt": "debiti_finanziari",
    "debiti_totali": "debiti_finanziari",
    # patrimonio netto
    "patrimonio_netto": "patrimonio_netto",
    "equity": "patrimonio_netto",
    "total_equity": "patrimonio_netto",
    # totale attivo
    "totale_attivo": "totale_attivo",
    "total_assets": "totale_attivo",
    # costo personale
    "costo_personale": "costo_personale",
    "labor_cost": "costo_personale",
    "costi_personale": "costo_personale",
    # costo materie
    "costo_materie": "costo_materie",
    "costo_materie_prime": "costo_materie",
    "acquisti": "costo_materie",
    "cogs": "costo_materie",
    # costi operativi
    "costi_operativi": "costi_operativi",
    "opex": "costi_operativi",
    "costi_generali": "costi_operativi",
    # oneri finanziari
    "oneri_finanziari": "oneri_finanziari",
    "interest_expense": "oneri_finanziari",
    "interessi_passivi": "oneri_finanziari",
    # cash operativo
    "cash_operativo": "cash_operativo",
    "cash_flow_operativo": "cash_operativo",
    "operating_cashflow": "cash_operativo",
    # cash corrente
    "cash_corrente": "cash_corrente",
    "liquidita": "cash_corrente",
    "disponibilita_liquide": "cash_corrente",
    "cash": "cash_corrente",
}

DEFAULTS = {
    "fatturato": 0.0, "ebitda": 0.0, "ebit": 0.0, "utile_netto": 0.0,
    "fatturato_prev": 0.0, "attivo_corrente": 0.0, "passivo_corrente": 0.0,
    "debiti_finanziari": 0.0, "patrimonio_netto": 0.0, "totale_attivo": 0.0,
    "costo_personale": 0.0, "costo_materie": 0.0, "costi_operativi": 0.0,
    "oneri_finanziari": 0.0, "cash_operativo": 0.0, "cash_corrente": 0.0,
}


def _parse_uploaded_file(uploaded_file) -> dict | None:
    """Legge CSV o Excel e restituisce dict con i valori finanziari."""
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            raw = uploaded_file.read()
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    df = pd.read_csv(io.BytesIO(raw), encoding=enc, header=None)
                    break
                except Exception:
                    continue
        else:
            df = pd.read_excel(io.BytesIO(uploaded_file.read()), header=None)
    except Exception as e:
        st.error(f"Errore lettura file: {e}")
        return None

    # Prova a trovare struttura: colonna chiave + colonna valore
    parsed = dict(DEFAULTS)
    company_name = ""

    for _, row in df.iterrows():
        if len(row) < 2:
            continue
        key_raw = str(row.iloc[0]).strip().lower().replace(" ", "_").replace("(€)", "").replace("(", "").replace(")", "")
        val_raw = row.iloc[1]
        # cerca nome azienda
        if "azienda" in key_raw or "company" in key_raw or "nome" in key_raw:
            company_name = str(val_raw).strip()
            continue
        # mappa il campo
        mapped = FIELD_MAP.get(key_raw)
        if mapped:
            try:
                parsed[mapped] = float(str(val_raw).replace(",", ".").replace(".", "").replace(",", ".") if "," in str(val_raw) else str(val_raw).replace(",", ""))
            except Exception:
                try:
                    parsed[mapped] = float(val_raw)
                except Exception:
                    pass

    return {"data": parsed, "company_name": company_name or "Azienda"}


def _get_cr_template_csv() -> bytes:
    """Template CSV scaricabile per Credit Readiness."""
    lines = [
        "campo,valore",
        "azienda,Nome Azienda Srl",
        "fatturato,2000000",
        "ebitda,200000",
        "ebit,140000",
        "utile_netto,80000",
        "fatturato_prev,1800000",
        "attivo_corrente,600000",
        "passivo_corrente,450000",
        "debiti_finanziari,350000",
        "patrimonio_netto,400000",
        "totale_attivo,950000",
        "costo_personale,680000",
        "costo_materie,820000",
        "costi_operativi,280000",
        "oneri_finanziari,52000",
        "cash_operativo,180000",
        "cash_corrente,95000",
    ]
    return "\n".join(lines).encode("utf-8")


# ─── Render risultati (condiviso tra upload e form) ───────────────────────────

def _render_results(result: CreditReadinessResult, company_name: str = ""):
    """Mostra tutti i risultati Credit Readiness."""

    status_class = f"status-{result.stato}"
    stato_icon = "✅" if result.stato == "finanziabile" else "⚠️" if result.stato == "borderline" else "🚫"
    if company_name:
        st.markdown(f"**🏢 {company_name}**")
    st.markdown(
        f'<div class="{status_class}">{stato_icon} {result.messaggio_principale}</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI principali
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        score_color = "green" if result.credit_score >= 70 else "orange" if result.credit_score >= 50 else "red"
        st.markdown(f"""
        <div class="metric-card {score_color}">
            <div class="metric-label">Credit Score</div>
            <div class="metric-value">{result.rating_emoji} {result.credit_score:.0f}/100</div>
            <div class="metric-sub">Rating: {result.rating} — {result.rating_label}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Credito Oggi</div>
            <div class="metric-value">{fmt_eur(result.credito_oggi_eur)}</div>
            <div class="metric-sub">Accesso immediato al credito</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-label">🚀 Credito Potenziale</div>
            <div class="metric-value">{fmt_eur(result.credito_potenziale_eur)}</div>
            <div class="metric-sub">+{fmt_eur(result.delta_credito_eur)} dopo ottimizzazione</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        crisi_label = f"tra {result.mesi_alla_crisi} mesi" if result.mesi_alla_crisi else "nessuna rilevata"
        crisi_color = "red" if result.mesi_alla_crisi and result.mesi_alla_crisi <= 3 else "orange" if result.mesi_alla_crisi else "green"
        st.markdown(f"""
        <div class="metric-card {crisi_color}">
            <div class="metric-label">⚠️ Crisi Imminente</div>
            <div class="metric-value">{"🔴" if crisi_color == "red" else "🟠" if crisi_color == "orange" else "🟢"} {crisi_label}</div>
            <div class="metric-sub">Rischio default: {result.rischio_default_pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Grafici
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.plotly_chart(gauge_chart(result.credit_score, result.rating), use_container_width=True)
    with col2:
        st.markdown("**💰 Credito: Oggi vs Potenziale**")
        st.plotly_chart(credit_bar_chart(result.credito_oggi_eur, result.credito_potenziale_eur), use_container_width=True)
        st.markdown(f"""
        <div style="background:#f8fafc;border-radius:8px;padding:0.7rem 1rem;font-size:0.85rem;color:#475569;">
        📊 EBITDA attuale: <b>{fmt_eur(result.ebitda_attuale)}</b> &nbsp;→&nbsp;
        Potenziale: <b>{fmt_eur(result.ebitda_potenziale)}</b>
        (+{fmt_eur(result.ebitda_gap)} ottimizzando i costi)
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("**🎯 Score Breakdown**")
        st.plotly_chart(score_breakdown_chart(result.score_breakdown), use_container_width=True)

    with st.expander("📋 Dettaglio Score per dimensione"):
        max_vals = {"EBITDA Margin": 25, "Debt / EBITDA": 20, "Liquidità Corrente": 20,
                    "Cash Flow Operativo": 15, "Solidità Patrimoniale": 12, "Trend Ricavi": 8}
        for dim, score in result.score_breakdown.items():
            mx = max_vals.get(dim, 20)
            pct = score / mx
            color = "#22c55e" if pct >= 0.7 else "#f59e0b" if pct >= 0.4 else "#ef4444"
            st.markdown(f"""
            <div style="margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.2rem;">
                    <span style="color:#1e293b;font-weight:500;">{dim}</span>
                    <span style="color:{color};font-weight:700;">{score:.0f}/{mx}</span>
                </div>
                <div style="background:#f1f5f9;border-radius:4px;height:8px;">
                    <div style="background:{color};width:{pct*100:.0f}%;height:8px;border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Azioni EBITDA Booster
    st.markdown("---")
    st.markdown("### 🔥 Azioni Prioritarie — EBITDA Booster")
    st.caption("Ogni azione è collegata direttamente all'incremento di credito ottenibile")

    if result.azioni:
        for i, action in enumerate(result.azioni, 1):
            diff_color = "#ef4444" if action.difficolta == "Alta" else "#f59e0b" if action.difficolta == "Media" else "#22c55e"
            st.markdown(f"""
            <div class="action-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div class="action-title">#{i} {action.categoria}</div>
                        <div class="action-impact">{action.descrizione}</div>
                    </div>
                    <div style="text-align:right;white-space:nowrap;padding-left:1rem;">
                        <div style="font-size:0.75rem;color:#64748b;">Difficoltà</div>
                        <div style="font-weight:600;color:{diff_color};">{action.difficolta}</div>
                        <div style="font-size:0.75rem;color:#64748b;margin-top:0.3rem;">Timeline</div>
                        <div style="font-weight:600;color:#475569;">{action.timeline_mesi} mesi</div>
                    </div>
                </div>
                <div style="display:flex;gap:1.5rem;margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid #f1f5f9;">
                    <div>
                        <span style="font-size:0.75rem;color:#64748b;">Taglio consigliato</span><br>
                        <span style="font-weight:700;color:#0f172a;">-{action.taglio_consigliato_pct:.1f}%</span>
                    </div>
                    <div>
                        <span style="font-size:0.75rem;color:#64748b;">+ EBITDA</span><br>
                        <span style="font-weight:700;color:#22c55e;">+{fmt_eur(action.impatto_ebitda_eur)}</span>
                    </div>
                    <div>
                        <span style="font-size:0.75rem;color:#64748b;">+ Credito bancario</span><br>
                        <span style="font-weight:700;color:#3b82f6;">+{fmt_eur(action.impatto_credito_eur)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Nessuna ottimizzazione critica rilevata — la struttura dei costi è nella norma.")

    # Crisis Detector
    if result.segnali:
        st.markdown("---")
        st.markdown("### ⚠️ Crisis Detector")
        st.caption("Segnali di rischio rilevati — agire prima che diventino problemi bancari")
        for segnale in result.segnali:
            css_class = "crisis-card critica" if segnale.severita == "Critica" else "crisis-card"
            timeline_str = f"Crisi prevista tra **{segnale.mesi_alla_crisi} mesi**" if segnale.mesi_alla_crisi else ""
            prob_color = "#ef4444" if segnale.probabilita_pct >= 60 else "#f59e0b"
            st.markdown(f"""
            <div class="{css_class}">
                <div style="display:flex;justify-content:space-between;">
                    <div style="font-weight:600;color:#1e293b;">{segnale.tipo}</div>
                    <div style="font-size:0.82rem;font-weight:600;color:{prob_color};">
                        Probabilità: {segnale.probabilita_pct:.0f}%
                    </div>
                </div>
                <div style="font-size:0.88rem;color:#475569;margin-top:0.4rem;">{segnale.descrizione}</div>
                {f'<div style="font-size:0.85rem;color:#dc2626;font-weight:600;margin-top:0.4rem;">📅 {timeline_str}</div>' if timeline_str else ''}
            </div>
            """, unsafe_allow_html=True)

    # Piano d'azione
    st.markdown("---")
    st.markdown("### 📋 Piano d'Azione — Roadmap verso il Credito")
    if result.azioni:
        total_ebitda_boost = sum(a.impatto_ebitda_eur for a in result.azioni)
        total_credit_boost = sum(a.impatto_credito_eur for a in result.azioni)
        max_timeline = max(a.timeline_mesi for a in result.azioni)
        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 EBITDA aggiuntivo totale", fmt_eur(total_ebitda_boost))
        col2.metric("💰 Credito sbloccabile", fmt_eur(total_credit_boost),
                    f"+{(total_credit_boost/max(result.credito_oggi_eur,1)*100):.0f}% vs oggi" if result.credito_oggi_eur > 0 else "")
        col3.metric("⏱️ Tempo per ottimizzazione completa", f"{max_timeline} mesi")
        st.info(f"""
        **Percorso consigliato:**  
        1. Inizia dalle azioni con difficoltà **Bassa** — risultati rapidi in 2-3 mesi  
        2. Affronta le azioni **Media** — impatto significativo sul credito bancario  
        3. Pianifica le azioni **Alta** — trasformazione strutturale per il lungo termine  
        
        Con queste ottimizzazioni puoi passare da **{fmt_eur(result.credito_oggi_eur)}** a **{fmt_eur(result.credito_potenziale_eur)}** di capacità creditizia in {max_timeline} mesi.
        """)
    else:
        st.success("✅ La struttura aziendale è già ottimizzata. Mantieni questi livelli per consolidare il rating.")

    # Footer export
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📄 Esporta PDF", use_container_width=True, key="cr_pdf_btn"):
            st.info("Export PDF disponibile nel modulo Audit Report — include il Credit Readiness completo.")


# ─── Render principale ────────────────────────────────────────────────────────

def render_credit_readiness():
    """Schermata principale Credit Readiness"""

    st.markdown("""
    <style>
    .cr-hero { background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
               padding: 2rem; border-radius: 16px; color: white; margin-bottom: 1.5rem; }
    .cr-hero h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .cr-hero p  { color: #94a3b8; margin: 0.3rem 0 0 0; }

    .upload-zone { background: linear-gradient(135deg, #f0fdf4, #dcfce7);
                   border: 2px dashed #22c55e; border-radius: 14px;
                   padding: 1.5rem; margin-bottom: 1.2rem; }
    .upload-zone h3 { color: #166534; margin: 0 0 0.3rem 0; font-size: 1.1rem; }
    .upload-zone p  { color: #4ade80; margin: 0; font-size: 0.85rem; }

    .metric-card { background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
                   box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #3b82f6; }
    .metric-card.green  { border-left-color: #22c55e; }
    .metric-card.orange { border-left-color: #f59e0b; }
    .metric-card.red    { border-left-color: #ef4444; }
    .metric-label { font-size: 0.78rem; color: #64748b; font-weight: 600; text-transform: uppercase;
                    letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #0f172a; line-height: 1; }
    .metric-sub   { font-size: 0.8rem; color: #94a3b8; margin-top: 0.2rem; }

    .action-card { background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
                   margin-bottom: 0.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                   border-left: 4px solid #f59e0b; }
    .action-title { font-size: 1rem; font-weight: 600; color: #0f172a; }
    .action-impact { font-size: 0.85rem; color: #64748b; margin-top: 0.3rem; }

    .crisis-card { background: #fff7ed; border-radius: 12px; padding: 1rem 1.4rem;
                   margin-bottom: 0.7rem; border-left: 4px solid #f97316; }
    .crisis-card.critica { background: #fff1f2; border-left-color: #ef4444; }

    .status-finanziabile     { background: #dcfce7; color: #166534; border-radius: 8px;
                               padding: 0.8rem 1.2rem; font-weight: 600; font-size: 0.95rem; }
    .status-borderline       { background: #fef9c3; color: #854d0e; border-radius: 8px;
                               padding: 0.8rem 1.2rem; font-weight: 600; font-size: 0.95rem; }
    .status-non_finanziabile { background: #fee2e2; color: #991b1b; border-radius: 8px;
                               padding: 0.8rem 1.2rem; font-weight: 600; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="cr-hero">
        <h1>⚡ Credit Readiness Dashboard</h1>
        <p>Quanto credito puoi ottenere oggi — e cosa fare per sbloccare il tuo potenziale</p>
    </div>
    """, unsafe_allow_html=True)

    # ── TAB: Carica & Analizza | Form Manuale ────────────────────────────────
    tab_upload, tab_form = st.tabs(["⚡ Carica & Analizza", "📝 Inserisci Manualmente"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — CARICA & ANALIZZA
    # ════════════════════════════════════════════════════════════════════════
    with tab_upload:
        st.markdown("""
        <div class="upload-zone">
            <h3>⚡ Carica il bilancio — analisi immediata</h3>
            <p>CSV o Excel con i dati aziendali → Credit Score + Azioni + Crisis Detector in un click</p>
        </div>
        """, unsafe_allow_html=True)

        col_up, col_tmpl = st.columns([3, 1])
        with col_tmpl:
            st.download_button(
                "📥 Template CSV",
                data=_get_cr_template_csv(),
                file_name="template_credit_readiness.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_up:
            uploaded = st.file_uploader(
                "Carica CSV o Excel",
                type=["csv", "xlsx", "xls"],
                key="cr_upload",
                label_visibility="collapsed",
            )

        if uploaded is not None:
            parsed = _parse_uploaded_file(uploaded)
            if parsed:
                d = parsed["data"]
                company_name = parsed["company_name"]

                with st.spinner("⚡ Calcolo Credit Readiness in corso…"):
                    result: CreditReadinessResult = analyze_credit_readiness(
                        fatturato=d["fatturato"],
                        ebitda=d["ebitda"],
                        ebit=d["ebit"],
                        utile_netto=d["utile_netto"],
                        attivo_corrente=d["attivo_corrente"],
                        passivo_corrente=d["passivo_corrente"],
                        debiti_finanziari=d["debiti_finanziari"],
                        patrimonio_netto=d["patrimonio_netto"],
                        totale_attivo=d["totale_attivo"],
                        costo_personale=d["costo_personale"],
                        costo_materie_prime=d["costo_materie"],
                        costi_operativi=d["costi_operativi"],
                        oneri_finanziari=d["oneri_finanziari"],
                        cash_operativo=d["cash_operativo"],
                        cash_corrente=d["cash_corrente"],
                        fatturato_prev=d["fatturato_prev"],
                    )

                st.markdown("---")
                _render_results(result, company_name=company_name)
        else:
            st.info("👆 Carica un file CSV o Excel per vedere l'analisi Credit Readiness completa — istantanea, zero click.")

            # Mostra campi supportati
            with st.expander("📋 Campi supportati nel file"):
                st.markdown("""
                | Campo CSV | Descrizione |
                |---|---|
                | `fatturato` | Ricavi totali |
                | `ebitda` | EBITDA |
                | `ebit` | Reddito operativo |
                | `utile_netto` | Utile / perdita netta |
                | `fatturato_prev` | Fatturato anno precedente |
                | `attivo_corrente` | Attivo circolante |
                | `passivo_corrente` | Passivo a breve |
                | `debiti_finanziari` | Debiti finanziari totali |
                | `patrimonio_netto` | Equity (può essere negativo) |
                | `totale_attivo` | Totale attivo |
                | `costo_personale` | Costo del lavoro |
                | `costo_materie` | Acquisti / materie prime |
                | `costi_operativi` | Costi generali operativi |
                | `oneri_finanziari` | Interessi passivi |
                | `cash_operativo` | Cash flow operativo |
                | `cash_corrente` | Disponibilità liquide |
                """)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — FORM MANUALE (invariato, come prima)
    # ════════════════════════════════════════════════════════════════════════
    with tab_form:
        with st.expander("📋 Inserisci dati di bilancio", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📊 Conto Economico**")
                fatturato = st.number_input("Fatturato (€)", min_value=0.0, value=2_000_000.0, step=10_000.0, format="%.0f", key="cr_fatturato")
                ebitda = st.number_input("EBITDA (€)", value=200_000.0, step=5_000.0, format="%.0f", key="cr_ebitda")
                ebit = st.number_input("EBIT (€)", value=140_000.0, step=5_000.0, format="%.0f", key="cr_ebit")
                utile_netto = st.number_input("Utile Netto (€)", value=80_000.0, step=5_000.0, format="%.0f", key="cr_utile")
                fatturato_prev = st.number_input("Fatturato anno precedente (€)", min_value=0.0, value=1_800_000.0, step=10_000.0, format="%.0f", key="cr_fat_prev")

            with col2:
                st.markdown("**🏛️ Stato Patrimoniale**")
                attivo_corrente = st.number_input("Attivo Corrente (€)", min_value=0.0, value=600_000.0, step=10_000.0, format="%.0f", key="cr_ac")
                passivo_corrente = st.number_input("Passivo Corrente (€)", min_value=0.0, value=450_000.0, step=10_000.0, format="%.0f", key="cr_pc")
                debiti_finanziari = st.number_input("Debiti Finanziari Totali (€)", min_value=0.0, value=350_000.0, step=10_000.0, format="%.0f", key="cr_df")
                patrimonio_netto = st.number_input("Patrimonio Netto (€)", value=400_000.0, step=10_000.0, format="%.0f", key="cr_pn")
                totale_attivo = st.number_input("Totale Attivo (€)", min_value=0.0, value=950_000.0, step=10_000.0, format="%.0f", key="cr_ta")

            with col3:
                st.markdown("**💰 Costi Dettagliati**")
                costo_personale = st.number_input("Costo del Personale (€)", min_value=0.0, value=680_000.0, step=10_000.0, format="%.0f", key="cr_cp")
                costo_materie = st.number_input("Acquisti / Materie Prime (€)", min_value=0.0, value=820_000.0, step=10_000.0, format="%.0f", key="cr_cm")
                costi_operativi = st.number_input("Costi Operativi Generali (€)", min_value=0.0, value=280_000.0, step=5_000.0, format="%.0f", key="cr_co")
                oneri_finanziari = st.number_input("Oneri Finanziari (€)", min_value=0.0, value=52_000.0, step=1_000.0, format="%.0f", key="cr_of")
                cash_operativo = st.number_input("Cash Flow Operativo (€)", value=180_000.0, step=5_000.0, format="%.0f", key="cr_cfo")
                cash_corrente = st.number_input("Disponibilità Liquide (€)", min_value=0.0, value=95_000.0, step=5_000.0, format="%.0f", key="cr_liq")

        analizza = st.button("⚡ ANALIZZA CREDIT READINESS", type="primary", use_container_width=True, key="cr_analizza_btn")

        if not analizza:
            st.info("👆 Inserisci i dati di bilancio e clicca **Analizza** per ottenere il tuo Credit Score e le azioni prioritarie.")
        else:
            with st.spinner("Calcolo in corso…"):
                result: CreditReadinessResult = analyze_credit_readiness(
                    fatturato=fatturato,
                    ebitda=ebitda,
                    ebit=ebit,
                    utile_netto=utile_netto,
                    attivo_corrente=attivo_corrente,
                    passivo_corrente=passivo_corrente,
                    debiti_finanziari=debiti_finanziari,
                    patrimonio_netto=patrimonio_netto,
                    totale_attivo=totale_attivo,
                    costo_personale=costo_personale,
                    costo_materie_prime=costo_materie,
                    costi_operativi=costi_operativi,
                    oneri_finanziari=oneri_finanziari,
                    cash_operativo=cash_operativo,
                    cash_corrente=cash_corrente,
                    fatturato_prev=fatturato_prev,
                )

            st.markdown("---")
            _render_results(result)
