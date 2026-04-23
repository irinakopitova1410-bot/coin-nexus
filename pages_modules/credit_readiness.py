"""
NEXUS Finance Pro — Credit Readiness Dashboard
La schermata più importante: porta l'azienda da NON finanziabile → FINANZIABILE
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from engine.credit_readiness import analyze_credit_readiness, CreditReadinessResult


# ─── Helpers UI ──────────────────────────────────────────────────────────────

def fmt_eur(value: float) -> str:
    """Formatta numero come valuta italiana"""
    if abs(value) >= 1_000_000:
        return f"€{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"€{value/1_000:.0f}K"
    else:
        return f"€{value:.0f}"

def gauge_chart(score: float, rating: str) -> go.Figure:
    """Gauge chart Credit Score"""
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
    """Bar chart credito oggi vs potenziale"""
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
    """Radar chart decomposizione score"""
    categories = list(breakdown.keys())
    values = list(breakdown.values())
    
    # Normalizza su max possibili
    maxima = {
        "EBITDA Margin": 25,
        "Debt / EBITDA": 20,
        "Liquidità Corrente": 20,
        "Cash Flow Operativo": 15,
        "Solidità Patrimoniale": 12,
        "Trend Ricavi": 8,
    }
    normalized = [
        (v / maxima.get(c, 20)) * 100
        for c, v in zip(categories, values)
    ]
    
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


# ─── Render principale ────────────────────────────────────────────────────────

def render_credit_readiness():
    """Schermata principale Credit Readiness"""
    
    st.markdown("""
    <style>
    .cr-hero { background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
               padding: 2rem; border-radius: 16px; color: white; margin-bottom: 1.5rem; }
    .cr-hero h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .cr-hero p  { color: #94a3b8; margin: 0.3rem 0 0 0; }
    
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
    
    # ── Input dati ───────────────────────────────────────────────────────────
    
    with st.expander("📋 Inserisci dati di bilancio", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Conto Economico**")
            fatturato = st.number_input("Fatturato (€)", min_value=0.0, value=2_000_000.0, step=10_000.0, format="%.0f")
            ebitda = st.number_input("EBITDA (€)", value=200_000.0, step=5_000.0, format="%.0f")
            ebit = st.number_input("EBIT (€)", value=140_000.0, step=5_000.0, format="%.0f")
            utile_netto = st.number_input("Utile Netto (€)", value=80_000.0, step=5_000.0, format="%.0f")
            fatturato_prev = st.number_input("Fatturato anno precedente (€)", min_value=0.0, value=1_800_000.0, step=10_000.0, format="%.0f")
        
        with col2:
            st.markdown("**🏛️ Stato Patrimoniale**")
            attivo_corrente = st.number_input("Attivo Corrente (€)", min_value=0.0, value=600_000.0, step=10_000.0, format="%.0f")
            passivo_corrente = st.number_input("Passivo Corrente (€)", min_value=0.0, value=450_000.0, step=10_000.0, format="%.0f")
            debiti_finanziari = st.number_input("Debiti Finanziari Totali (€)", min_value=0.0, value=350_000.0, step=10_000.0, format="%.0f")
            patrimonio_netto = st.number_input("Patrimonio Netto (€)", min_value=0.0, value=400_000.0, step=10_000.0, format="%.0f")
            totale_attivo = st.number_input("Totale Attivo (€)", min_value=0.0, value=950_000.0, step=10_000.0, format="%.0f")
        
        with col3:
            st.markdown("**💰 Costi Dettagliati**")
            costo_personale = st.number_input("Costo del Personale (€)", min_value=0.0, value=680_000.0, step=10_000.0, format="%.0f")
            costo_materie = st.number_input("Acquisti / Materie Prime (€)", min_value=0.0, value=820_000.0, step=10_000.0, format="%.0f")
            costi_operativi = st.number_input("Costi Operativi Generali (€)", min_value=0.0, value=280_000.0, step=5_000.0, format="%.0f")
            oneri_finanziari = st.number_input("Oneri Finanziari (€)", min_value=0.0, value=52_000.0, step=1_000.0, format="%.0f")
            cash_operativo = st.number_input("Cash Flow Operativo (€)", value=180_000.0, step=5_000.0, format="%.0f")
            cash_corrente = st.number_input("Disponibilità Liquide (€)", min_value=0.0, value=95_000.0, step=5_000.0, format="%.0f")
    
    analizza = st.button("⚡ ANALIZZA CREDIT READINESS", type="primary", use_container_width=True)
    
    if not analizza:
        st.info("👆 Inserisci i dati di bilancio e clicca **Analizza** per ottenere il tuo Credit Score e le azioni prioritarie.")
        return
    
    # ── Calcolo ──────────────────────────────────────────────────────────────
    
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SEZIONE 1 — STATUS + KPI principali
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("---")
    
    # Messaggio principale
    status_class = f"status-{result.stato}"
    stato_icon = "✅" if result.stato == "finanziabile" else "⚠️" if result.stato == "borderline" else "🚫"
    st.markdown(
        f'<div class="{status_class}">{stato_icon} {result.messaggio_principale}</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI cards principali
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SEZIONE 2 — Gauge + Credito chart + Radar
    # ═══════════════════════════════════════════════════════════════════════
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.plotly_chart(
            gauge_chart(result.credit_score, result.rating),
            use_container_width=True,
        )
    
    with col2:
        st.markdown("**💰 Credito: Oggi vs Potenziale**")
        st.plotly_chart(
            credit_bar_chart(result.credito_oggi_eur, result.credito_potenziale_eur),
            use_container_width=True,
        )
        # EBITDA detail
        st.markdown(f"""
        <div style="background:#f8fafc;border-radius:8px;padding:0.7rem 1rem;font-size:0.85rem;color:#475569;">
        📊 EBITDA attuale: <b>{fmt_eur(result.ebitda_attuale)}</b> &nbsp;→&nbsp;
        Potenziale: <b>{fmt_eur(result.ebitda_potenziale)}</b>
        (+{fmt_eur(result.ebitda_gap)} ottimizzando i costi)
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("**🎯 Score Breakdown**")
        st.plotly_chart(
            score_breakdown_chart(result.score_breakdown),
            use_container_width=True,
        )
    
    # Score breakdown dettaglio
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SEZIONE 3 — Azioni prioritarie (EBITDA Booster)
    # ═══════════════════════════════════════════════════════════════════════
    
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SEZIONE 4 — Crisis Detector
    # ═══════════════════════════════════════════════════════════════════════
    
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SEZIONE 5 — Piano d'azione sintetico
    # ═══════════════════════════════════════════════════════════════════════
    
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
        if st.button("📄 Esporta PDF", use_container_width=True):
            st.info("Export PDF disponibile nel modulo Audit Report — include il Credit Readiness completo.")
