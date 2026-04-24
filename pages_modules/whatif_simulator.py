"""
What-If Simulator — Scenari interattivi con slider
"Cosa succede se il costo delle materie prime aumenta del 15%?"
Aggiornamento istantaneo Z-Score, EBITDA, Probabilità Default
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io


# ─── Calcoli core ─────────────────────────────────────────────────────────────
def calcola_zscore(ccn, ebit, utili_nd, pn, ricavi, totale_attivo, debiti_totali):
    """Altman Z'-Score per aziende non quotate."""
    if totale_attivo <= 0:
        return 0.0
    x1 = ccn / totale_attivo
    x2 = utili_nd / totale_attivo
    x3 = ebit / totale_attivo
    x4 = pn / max(debiti_totali, 1)
    x5 = ricavi / totale_attivo
    return round(0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.420 * x4 + 0.998 * x5, 3)


def prob_default(zscore):
    """Probabilità di default approssimativa da Z-Score."""
    if zscore > 2.99:
        return max(2.0, 10 - zscore * 2)
    elif zscore >= 1.81:
        return 20 + (2.99 - zscore) * 30
    else:
        return min(95.0, 70 + (1.81 - zscore) * 15)


def zona_zscore(zscore):
    if zscore > 2.99:
        return "🟢 Zona Sicura", "#22c55e"
    elif zscore >= 1.81:
        return "🟡 Zona Grigia", "#f59e0b"
    else:
        return "🔴 Zona Distress", "#ef4444"


def calcola_scenario(base: dict, shock: dict) -> dict:
    """Applica gli shock percentuali ai dati base e ricalcola tutti i KPI."""
    # Applica shock
    fatturato_new = base["fatturato"] * (1 + shock.get("delta_fatturato", 0) / 100)
    costi_mat_new = base["costi_materie"] * (1 + shock.get("delta_costi_mat", 0) / 100)
    costi_pers_new = base["costi_personale"] * (1 + shock.get("delta_costi_pers", 0) / 100)
    debiti_new = base["totale_debiti"] * (1 + shock.get("delta_debiti", 0) / 100)
    clienti_new = base.get("crediti_clienti", base["fatturato"] * 0.2) * (
        1 + shock.get("delta_crediti", 0) / 100)
    tasso_new = base.get("tasso_interesse", 0.04) + shock.get("delta_tasso", 0) / 100

    # EBITDA scenario
    ebitda_base_orig = base.get("ebitda", fatturato_new * 0.12)
    costi_totali_orig = base["costi_materie"] + base["costi_personale"]
    costi_totali_new  = costi_mat_new + costi_pers_new
    delta_costi = costi_totali_new - costi_totali_orig
    delta_ricavi = fatturato_new - base["fatturato"]
    ebitda_new = ebitda_base_orig + delta_ricavi - delta_costi

    # Interessi nuovi
    interessi_new = debiti_new * tasso_new

    # Z-Score scenario
    ammort = base.get("ammortamenti", ebitda_base_orig * 0.3)
    ebit_new = ebitda_new - ammort
    pn_new = base["patrimonio_netto"] + (ebitda_new - ebitda_base_orig) * 0.5
    ccn_new = base.get("capitale_circolante_netto", 0) + delta_ricavi * 0.1 - (clienti_new - base.get("crediti_clienti", 0))
    utili_nd = base.get("utili_non_distribuiti", pn_new * 0.3)

    zscore_new = calcola_zscore(
        ccn_new, ebit_new, utili_nd, pn_new,
        fatturato_new, base["totale_attivo"], debiti_new
    )

    # DSCR
    servizio_debito = interessi_new + debiti_new * 0.08
    dscr_new = ebitda_new / servizio_debito if servizio_debito > 0 else 99.0

    return {
        "fatturato": fatturato_new,
        "ebitda": ebitda_new,
        "ebitda_margin": ebitda_new / fatturato_new * 100 if fatturato_new > 0 else 0,
        "ebit": ebit_new,
        "interessi": interessi_new,
        "debiti": debiti_new,
        "pn": pn_new,
        "zscore": zscore_new,
        "prob_default": prob_default(zscore_new),
        "dscr": round(dscr_new, 3),
    }


# ─── Grafici ─────────────────────────────────────────────────────────────────
def grafico_confronto(base_kpi: dict, scenario_kpi: dict) -> go.Figure:
    metriche = ["EBITDA (€)", "EBITDA Margin (%)", "Z-Score", "Prob. Default (%)"]
    val_base = [
        base_kpi.get("ebitda", 0),
        base_kpi.get("ebitda_margin", 0),
        base_kpi.get("zscore", 0),
        base_kpi.get("prob_default", 0)
    ]
    val_scen = [
        scenario_kpi.get("ebitda", 0),
        scenario_kpi.get("ebitda_margin", 0),
        scenario_kpi.get("zscore", 0),
        scenario_kpi.get("prob_default", 0)
    ]

    fig = go.Figure(data=[
        go.Bar(name="📊 Base", x=metriche, y=val_base,
               marker_color="#6366f1", opacity=0.8),
        go.Bar(name="🔮 Scenario", x=metriche, y=val_scen,
               marker_color="#f59e0b", opacity=0.9),
    ])
    fig.update_layout(
        barmode="group",
        title="📊 Base vs Scenario — Confronto KPI",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def grafico_waterfall_ebitda(base_ebitda, delta_ricavi, delta_materie, delta_personale, scen_ebitda) -> go.Figure:
    fig = go.Figure(go.Waterfall(
        name="EBITDA Waterfall",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["EBITDA Base", "Δ Fatturato", "Δ Costi Materie", "Δ Costi Personale", "EBITDA Scenario"],
        textposition="outside",
        y=[base_ebitda, delta_ricavi, -delta_materie, -delta_personale, 0],
        connector={"line": {"color": "#6366f1"}},
        increasing={"marker": {"color": "#22c55e"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#f59e0b"}},
    ))
    fig.update_layout(
        title="💰 Waterfall EBITDA — Impatto delle variazioni",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        showlegend=False
    )
    return fig


# ─── Parse CSV ───────────────────────────────────────────────────────────────
def parse_csv_whatif(uploaded_file) -> dict | None:
    try:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        uploaded_file.seek(0)
        lines = [l for l in content.splitlines() if not l.strip().startswith("#") and l.strip()]
        df = pd.read_csv(io.StringIO("\n".join(lines)), header=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        val_col = "valore" if "valore" in df.columns else df.columns[1]
        data = {str(r[df.columns[0]]).strip().lower(): r[val_col]
                for _, r in df.iterrows() if pd.notna(r[val_col])}

        def g(keys, default=0.0):
            for k in keys:
                if k in data:
                    try:
                        return float(str(data[k]).replace(".", "").replace(",", ".").strip())
                    except:
                        pass
            return default

        fat = g(["fatturato", "ricavi_netti", "ricavi_vendite"])
        ebitda = g(["ebitda"])
        return {
            "azienda": str(data.get("azienda", data.get("nome_azienda", "Azienda"))),
            "fatturato": fat,
            "ebitda": ebitda if ebitda != 0 else fat * 0.12,
            "ebit": g(["ebit", "risultato_operativo"]),
            "costi_materie": g(["costi_materie", "costi_materie_prime", "acquisti"]),
            "costi_personale": g(["costi_personale", "costo_lavoro"]),
            "totale_debiti": g(["totale_debiti", "passivo_totale"]),
            "totale_attivo": g(["totale_attivo"]),
            "patrimonio_netto": g(["patrimonio_netto", "equity"]),
            "capitale_circolante_netto": g(["capitale_circolante_netto", "ccn"]),
            "utili_non_distribuiti": g(["utili_non_distribuiti", "riserve"]),
            "ammortamenti": g(["ammortamenti"]),
            "crediti_clienti": g(["crediti_clienti", "crediti_vs_clienti"]),
            "tasso_interesse": g(["tasso_interesse"], 0.04),
        }
    except Exception as e:
        st.error(f"Errore parsing: {e}")
        return None


# ─── UI ──────────────────────────────────────────────────────────────────────
def show_whatif_simulator():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0369a1, #0284c7);
                padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.8rem;'>🔮 What-If Simulator</h2>
        <p style='color: rgba(255,255,255,0.85); margin: 0.3rem 0 0;'>
            Scenari interattivi · "Cosa succede se...?" · Aggiornamento istantaneo Z-Score e default
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_manuale = st.tabs(["⚡ Carica & Simula", "📝 Inserisci Base Manualmente"])

    with tab_upload:
        _tab_upload_whatif()
    with tab_manuale:
        _tab_manuale_whatif()


def _mostra_simulatore(base: dict):
    """Mostra i slider What-If e aggiorna i KPI in tempo reale."""
    azienda = base.get("azienda", "Azienda")

    # Calcola KPI base
    ebitda_margin_base = base["ebitda"] / base["fatturato"] * 100 if base["fatturato"] > 0 else 0
    ammort = base.get("ammortamenti", base["ebitda"] * 0.3)
    ebit_base = base["ebitda"] - ammort
    zscore_base = calcola_zscore(
        base.get("capitale_circolante_netto", 0),
        ebit_base,
        base.get("utili_non_distribuiti", base["patrimonio_netto"] * 0.3),
        base["patrimonio_netto"],
        base["fatturato"],
        base["totale_attivo"],
        base["totale_debiti"]
    )
    base_kpi = {
        "ebitda": base["ebitda"],
        "ebitda_margin": ebitda_margin_base,
        "zscore": zscore_base,
        "prob_default": prob_default(zscore_base)
    }

    st.markdown(f"---\n### 🔮 Simulatore What-If — **{azienda}**")

    # Dati base
    col1, col2, col3, col4 = st.columns(4)
    zona_b, color_b = zona_zscore(zscore_base)
    with col1:
        st.metric("Fatturato base", f"€{base['fatturato']:,.0f}")
    with col2:
        st.metric("EBITDA base", f"€{base['ebitda']:,.0f}", f"{ebitda_margin_base:.1f}%")
    with col3:
        st.metric("Z-Score base", f"{zscore_base:.2f}", zona_b)
    with col4:
        st.metric("Prob. Default base", f"{prob_default(zscore_base):.1f}%")

    st.markdown("---\n### 🎛️ Imposta lo scenario")
    st.info("Muovi gli slider per vedere **istantaneamente** come cambiano Z-Score, EBITDA e probabilità di default.")

    # Scenari predefiniti
    col_pre = st.columns(5)
    scenari_preset = {
        "📉 Recessione -20%": {"delta_fatturato": -20, "delta_costi_mat": 10, "delta_tasso": 1},
        "🔥 +15% Materie": {"delta_costi_mat": 15},
        "👥 Perdo cliente": {"delta_fatturato": -30, "delta_crediti": -30},
        "📈 Espansione +25%": {"delta_fatturato": 25, "delta_costi_pers": 10},
        "🏦 Tassi +2%": {"delta_tasso": 2},
    }
    preset_selezionato = None
    for i, (nome, shock) in enumerate(scenari_preset.items()):
        with col_pre[i]:
            if st.button(nome, use_container_width=True, key=f"preset_{i}"):
                preset_selezionato = shock

    # Sliders
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        delta_fat  = st.slider("📈 Variazione fatturato (%)", -50, 50,
                               preset_selezionato.get("delta_fatturato", 0) if preset_selezionato else 0)
        delta_mat  = st.slider("🏭 Variazione costi materie prime (%)", -30, 50,
                               preset_selezionato.get("delta_costi_mat", 0) if preset_selezionato else 0)
        delta_pers = st.slider("👥 Variazione costi personale (%)", -20, 30,
                               preset_selezionato.get("delta_costi_pers", 0) if preset_selezionato else 0)
    with col_s2:
        delta_deb  = st.slider("🏦 Variazione debiti (%)", -30, 50,
                               preset_selezionato.get("delta_debiti", 0) if preset_selezionato else 0)
        delta_cred = st.slider("📋 Variazione crediti clienti (%)", -40, 40,
                               preset_selezionato.get("delta_crediti", 0) if preset_selezionato else 0)
        delta_tasso= st.slider("💹 Variazione tasso interesse (pp)", -2, 5,
                               preset_selezionato.get("delta_tasso", 0) if preset_selezionato else 0)

    shock = {
        "delta_fatturato": delta_fat,
        "delta_costi_mat": delta_mat,
        "delta_costi_pers": delta_pers,
        "delta_debiti": delta_deb,
        "delta_crediti": delta_cred,
        "delta_tasso": float(delta_tasso),
    }

    # Calcola scenario
    scen = calcola_scenario(base, shock)
    zona_s, color_s = zona_zscore(scen["zscore"])

    # Risultati scenario
    st.markdown("---\n### 📊 Risultati Scenario")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    def delta_metric(label, base_val, scen_val, fmt="€{:,.0f}", invert=False):
        delta_v = scen_val - base_val
        delta_pct = delta_v / abs(base_val) * 100 if base_val != 0 else 0
        delta_str = f"{'+' if delta_v >= 0 else ''}{delta_pct:.1f}%"
        color = "normal" if (delta_v >= 0) != invert else "inverse"
        st.metric(label, fmt.format(scen_val), delta_str, delta_color=color)

    with col_r1:
        delta_metric("Fatturato scenario", base["fatturato"], scen["fatturato"])
    with col_r2:
        delta_metric("EBITDA scenario", base["ebitda"], scen["ebitda"])
    with col_r3:
        delta_z = scen["zscore"] - zscore_base
        st.metric("Z-Score scenario", f"{scen['zscore']:.2f}",
                  f"{'+' if delta_z >= 0 else ''}{delta_z:.2f} → {zona_s}")
    with col_r4:
        delta_metric("Prob. Default", prob_default(zscore_base), scen["prob_default"],
                     fmt="{:.1f}%", invert=True)

    # Alert scenario
    if scen["zscore"] < 1.81 and zscore_base >= 1.81:
        st.error("🚨 **ATTENZIONE**: Questo scenario porta l'azienda in **Zona Distress**! "
                "Probabilità di default elevata — attivare subito le misure CCII.")
    elif scen["dscr"] < 1.0:
        st.warning(f"⚠️ **DSCR = {scen['dscr']:.2f}x** — Sotto la soglia legale (1.0x). "
                  "Il flusso di cassa non copre il servizio del debito.")
    elif scen["ebitda"] < 0:
        st.error("🔴 **EBITDA negativo** in questo scenario — l'azienda brucia cassa nella gestione ordinaria.")
    elif scen["zscore"] > 2.99 and zscore_base <= 2.99:
        st.success("🎉 **Ottimo!** Questo scenario porta l'azienda in **Zona Sicura** — finanziamento facilitato!")

    # Grafici
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        scen_kpi = {
            "ebitda": scen["ebitda"],
            "ebitda_margin": scen["ebitda_margin"],
            "zscore": scen["zscore"],
            "prob_default": scen["prob_default"]
        }
        st.plotly_chart(grafico_confronto(base_kpi, scen_kpi), use_container_width=True)
    with col_g2:
        delta_ricavi_val = scen["fatturato"] - base["fatturato"]
        delta_mat_val  = base["costi_materie"] * (delta_mat / 100)
        delta_pers_val = base["costi_personale"] * (delta_pers / 100)
        st.plotly_chart(grafico_waterfall_ebitda(
            base["ebitda"], delta_ricavi_val, delta_mat_val, delta_pers_val, scen["ebitda"]
        ), use_container_width=True)

    # Tabella riepilogo
    with st.expander("📋 Tabella riepilogo completa"):
        riepilogo = pd.DataFrame({
            "KPI": ["Fatturato", "EBITDA", "EBITDA Margin", "Z-Score", "Prob. Default", "DSCR"],
            "Base": [f"€{base['fatturato']:,.0f}", f"€{base['ebitda']:,.0f}",
                    f"{ebitda_margin_base:.1f}%", f"{zscore_base:.2f}",
                    f"{prob_default(zscore_base):.1f}%", "n.d."],
            "Scenario": [f"€{scen['fatturato']:,.0f}", f"€{scen['ebitda']:,.0f}",
                        f"{scen['ebitda_margin']:.1f}%", f"{scen['zscore']:.2f}",
                        f"{scen['prob_default']:.1f}%", f"{scen['dscr']:.2f}x"],
            "Δ": [
                f"{delta_fat:+.0f}%", f"€{scen['ebitda']-base['ebitda']:+,.0f}",
                f"{scen['ebitda_margin']-ebitda_margin_base:+.1f}pp",
                f"{scen['zscore']-zscore_base:+.2f}",
                f"{scen['prob_default']-prob_default(zscore_base):+.1f}%",
                "-"
            ]
        })
        st.dataframe(riepilogo, use_container_width=True, hide_index=True)


def _tab_upload_whatif():
    template = """campo,valore
azienda,La Mia SRL
fatturato,3000000
ebitda,360000
costi_materie,1200000
costi_personale,800000
totale_debiti,2000000
totale_attivo,3500000
patrimonio_netto,1000000
capitale_circolante_netto,200000
utili_non_distribuiti,350000
ammortamenti,100000
crediti_clienti,400000
tasso_interesse,0.045
"""
    st.download_button("📥 Template CSV What-If", template,
                      "template_whatif.csv", "text/csv", use_container_width=True)

    uploaded = st.file_uploader("📂 Carica CSV o Excel dati azienda",
                                type=["csv", "xlsx", "xls"], key="whatif_upload")
    if uploaded:
        base = parse_csv_whatif(uploaded)
        if base:
            _mostra_simulatore(base)
        else:
            st.error("❌ File non riconosciuto. Usa il template CSV.")


def _tab_manuale_whatif():
    with st.form("whatif_base_form"):
        st.markdown("### 📝 Dati base azienda")
        col1, col2 = st.columns(2)
        with col1:
            azienda  = st.text_input("🏢 Nome azienda", "La Mia SRL")
            fatturato= st.number_input("Fatturato / Ricavi (€)", value=3000000.0, step=100000.0)
            ebitda   = st.number_input("EBITDA (€)", value=360000.0, step=10000.0)
            costi_mat= st.number_input("Costi materie prime (€)", value=1200000.0, step=50000.0, min_value=0.0)
            costi_pers=st.number_input("Costi personale (€)", value=800000.0, step=50000.0, min_value=0.0)
        with col2:
            tot_att  = st.number_input("Totale attivo (€)", value=3500000.0, step=100000.0)
            tot_deb  = st.number_input("Totale debiti (€)", value=2000000.0, step=100000.0, min_value=0.0)
            pn       = st.number_input("Patrimonio netto (€)", value=1000000.0, step=50000.0)
            ccn      = st.number_input("Capitale circolante netto (€)", value=200000.0, step=10000.0)
            utili_nd = st.number_input("Utili non distribuiti (€)", value=350000.0, step=10000.0)

        submitted = st.form_submit_button("🔮 Avvia Simulatore", use_container_width=True, type="primary")

    if submitted:
        base = {
            "azienda": azienda, "fatturato": fatturato, "ebitda": ebitda,
            "costi_materie": costi_mat, "costi_personale": costi_pers,
            "totale_attivo": tot_att, "totale_debiti": tot_deb,
            "patrimonio_netto": pn, "capitale_circolante_netto": ccn,
            "utili_non_distribuiti": utili_nd, "ammortamenti": ebitda * 0.28,
            "crediti_clienti": fatturato * 0.15, "tasso_interesse": 0.045,
        }
        _mostra_simulatore(base)
