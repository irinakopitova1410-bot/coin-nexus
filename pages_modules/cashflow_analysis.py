"""
NEXUS Finance Pro — Cash Flow Analysis Page
Rendiconto finanziario, proiezioni 5 anni, covenant, stress test.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
from engine.cashflow import calculate_cashflow
from engine.financial_ratios import REQUIRED_FIELDS, OPTIONAL_FIELDS
from utils.pdf_export import generate_full_report
from utils.file_parser import parse_financial_file


def _run_cashflow(data: dict, company_name: str):
    """Calcola e visualizza tutti i risultati Cash Flow."""

    cf = calculate_cashflow(data)

    # ── Alert ─────────────────────────────────────────────────────────────────
    for alert in cf.alerts:
        kind = "error" if "🔴" in alert else "warning"
        getattr(st, kind)(alert)

    # ── KPI principali ────────────────────────────────────────────────────────
    st.subheader("💡 KPI Cash Flow")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cash Flow Operativo", f"€ {cf.operating_cashflow:,.0f}",
                "🟢 Positivo" if cf.operating_cashflow > 0 else "🔴 Negativo")
    col2.metric("Free Cash Flow", f"€ {cf.free_cashflow:,.0f}",
                "🟢 Positivo" if cf.free_cashflow > 0 else "🔴 Negativo")
    col3.metric("FCF Margin", f"{cf.fcf_margin:.1%}", "vs revenue")
    col4.metric("Cash Conversion", f"{cf.cash_conversion_ratio:.2f}x", "OCF/Utile Netto")

    # ── Rendiconto finanziario ────────────────────────────────────────────────
    st.subheader("📋 Rendiconto Finanziario — Metodo Indiretto")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🔄 Area Operativa**")
        op_data = {
            "Utile Netto": cf.net_income,
            "(+) Ammortamenti": cf.depreciation,
            "(±) Δ Cap. Circolante": cf.delta_working_capital,
            "(±) Altre variazioni": cf.other_operating,
        }
        for k, v in op_data.items():
            color = "🟢" if v >= 0 else "🔴"
            st.markdown(f"{color} **{k}**: € {v:,.0f}")
        st.markdown("---")
        ocf_color = "🟢" if cf.operating_cashflow >= 0 else "🔴"
        st.markdown(f"**{ocf_color} = Cash Flow Operativo: € {cf.operating_cashflow:,.0f}**")

    with col2:
        st.markdown("**🏗️ Area Investimenti**")
        inv_data = {
            "(−) CapEx": -cf.capex,
            "(−) Acquisizioni": -cf.acquisitions,
        }
        for k, v in inv_data.items():
            color = "🟢" if v >= 0 else "🔴"
            st.markdown(f"{color} **{k}**: € {v:,.0f}")
        st.markdown("---")
        inv_color = "🟢" if cf.investing_cashflow >= 0 else "🔴"
        st.markdown(f"**{inv_color} = CF Investimenti: € {cf.investing_cashflow:,.0f}**")

    with col3:
        st.markdown("**🏦 Area Finanziaria**")
        fin_data = {
            "(+) Nuovi Debiti": cf.debt_issued,
            "(−) Rimborso Debiti": -cf.debt_repaid,
            "(−) Dividendi": -cf.dividends,
        }
        for k, v in fin_data.items():
            color = "🟢" if v >= 0 else "🔴"
            st.markdown(f"{color} **{k}**: € {v:,.0f}")
        st.markdown("---")
        fin_color = "🟢" if cf.financing_cashflow >= 0 else "🔴"
        st.markdown(f"**{fin_color} = CF Finanziario: € {cf.financing_cashflow:,.0f}**")

    net_color = "🟢" if cf.net_change >= 0 else "🔴"
    st.markdown(f"### {net_color} Variazione Netta Cassa: € {cf.net_change:,.0f}")

    # ── Waterfall Chart ───────────────────────────────────────────────────────
    st.subheader("📊 Waterfall Cash Flow")
    measures = ["relative", "relative", "relative", "total",
                "relative", "total",
                "relative", "relative", "relative", "total",
                "total"]
    x_labels = ["Utile Netto", "Ammortamenti", "Δ WC", "CF Operativo",
                 "CapEx", "Free CF",
                 "Nuovi Debiti", "Rimborso", "Dividendi", "CF Finanziario",
                 "Variazione Netta"]
    y_vals = [cf.net_income, cf.depreciation, cf.delta_working_capital,
              cf.operating_cashflow,
              -cf.capex, cf.free_cashflow,
              cf.debt_issued, -cf.debt_repaid, -cf.dividends,
              cf.financing_cashflow,
              cf.net_change]
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_vals,
        connector={"line": {"color": "#0D47A1"}},
        increasing={"marker": {"color": "#00C853"}},
        decreasing={"marker": {"color": "#D50000"}},
        totals={"marker": {"color": "#0D47A1"}},
        texttemplate="%{y:,.0f}",
        textposition="outside",
    ))
    fig_wf.update_layout(height=420, title="Cash Flow Waterfall (€)", showlegend=False)
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── Proiezioni ────────────────────────────────────────────────────────────
    st.subheader("📈 Proiezioni a 5 anni")
    df_proj = pd.DataFrame(cf.projections)
    st.dataframe(df_proj.style.format({
        "OCF Base": "€ {:,.0f}", "FCF Base": "€ {:,.0f}",
        "OCF Stress": "€ {:,.0f}", "FCF Stress": "€ {:,.0f}",
    }), use_container_width=True, hide_index=True)

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(x=df_proj["Anno"], y=df_proj["FCF Base"],
                                   name="FCF Base", mode="lines+markers",
                                   line=dict(color="#00C853", width=2)))
    fig_proj.add_trace(go.Scatter(x=df_proj["Anno"], y=df_proj["FCF Stress"],
                                   name="FCF Stress", mode="lines+markers",
                                   line=dict(color="#D50000", width=2, dash="dash")))
    fig_proj.add_trace(go.Scatter(x=df_proj["Anno"], y=df_proj["OCF Base"],
                                   name="OCF Base", mode="lines+markers",
                                   line=dict(color="#0D47A1", width=2)))
    fig_proj.update_layout(height=350, title="Free Cash Flow — Proiezioni 5 Anni")
    st.plotly_chart(fig_proj, use_container_width=True)

    # ── Covenant ─────────────────────────────────────────────────────────────
    if cf.covenants:
        st.subheader("🏦 Covenant Bancari")
        df_cov = pd.DataFrame(cf.covenants)
        st.dataframe(df_cov, use_container_width=True, hide_index=True)

    # ── KPI avanzati ──────────────────────────────────────────────────────────
    st.subheader("📐 KPI Avanzati")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("CapEx Intensity", f"{cf.capex_intensity:.1%}", "CapEx/Ricavi")
    kpi_col2.metric("Reinvestment Rate", f"{cf.reinvestment_rate:.1%}", "CapEx/(CapEx+FCF)")
    kpi_col3.metric("Cash Conversion", f"{cf.cash_conversion_ratio:.2f}x", "OCF/Utile Netto")
    kpi_col4.metric("FCF Margin", f"{cf.fcf_margin:.1%}", "FCF/Ricavi")

    # ── Export ────────────────────────────────────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Genera Report PDF", type="primary", use_container_width=True, key="cf_pdf_btn"):
            with st.spinner("Generazione PDF..."):
                try:
                    pdf_bytes = generate_full_report(
                        company_name=company_name or "Azienda",
                        cashflow_result=cf,
                        raw_data=data,
                    )
                    st.download_button("⬇️ Scarica PDF", data=pdf_bytes,
                                       file_name=f"cashflow_{company_name or 'report'}.pdf",
                                       mime="application/pdf", use_container_width=True)
                    st.success("✅ PDF pronto!")
                except Exception as e:
                    st.error(f"Errore PDF: {e}")
    with col2:
        csv_buf = io.StringIO()
        df_proj.to_csv(csv_buf, index=False)
        st.download_button("📊 Esporta Proiezioni CSV", data=csv_buf.getvalue().encode(),
                           file_name="proiezioni_cashflow.csv", mime="text/csv",
                           use_container_width=True)


def render_cashflow_analysis():
    st.title("💰 Cash Flow Analysis")
    st.markdown("Rendiconto finanziario con metodo indiretto, proiezioni a 5 anni e covenant bancari.")

    erp_data = st.session_state.get("erp_data", {})
    company_name = st.session_state.get("erp_company", "")

    tab_upload, tab_form = st.tabs(["⚡ Carica & Analizza", "📝 Form Manuale"])

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — CARICA & ANALIZZA
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_upload:
        st.markdown("### 📂 Carica il bilancio aziendale")
        st.markdown(
            "Carica un file **CSV, Excel o PDF** con i dati finanziari. "
            "L'analisi Cash Flow parte in automatico."
        )

        # Formato CSV atteso
        with st.expander("📋 Formato CSV atteso (clicca per vedere esempio)", expanded=False):
            st.markdown("""
Il CSV deve avere 2 o 3 colonne: `campo`, `valore`, (opzionale: `descrizione`).

```
campo,valore,descrizione
revenue,5000000,Ricavi netti
ebitda,800000,EBITDA
ebit,500000,EBIT
net_income,250000,Utile Netto
depreciation,300000,Ammortamenti
interest_expense,120000,Oneri Finanziari
tax_expense,80000,Imposte
total_assets,8000000,Totale Attivo
equity,2500000,Patrimonio Netto
total_debt,3000000,Debiti Finanziari
current_assets,2000000,Attivo Corrente
current_liabilities,1500000,Passivo Corrente
accounts_receivable,900000,Crediti Commerciali
accounts_payable,600000,Debiti Fornitori
inventory,400000,Magazzino
capex,350000,Investimenti
```

**Puoi anche usare il file demo:** `COIN_SPA_Bilancio_Completo_2025.csv`
            """)

        uploaded_file = st.file_uploader(
            "📎 Trascina qui il file oppure clicca per sceglierlo",
            type=["csv", "xlsx", "xls", "pdf"],
            key="cf_upload",
            help="Formati supportati: CSV (separato da virgola), Excel (.xlsx/.xls), PDF"
        )

        if uploaded_file is not None:
            st.info(f"📄 File caricato: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            with st.spinner("🔍 Analisi in corso..."):
                try:
                    parsed = parse_financial_file(uploaded_file)

                    if "error" in parsed:
                        st.error(f"❌ Errore nel parsing: {parsed['error']}")
                        st.stop()

                    # Mostra anteprima campi rilevati
                    detected_fields = {k: v for k, v in parsed.items()
                                       if k not in ("company_name", "error") and v != 0
                                       and isinstance(v, (int, float))}
                    if detected_fields:
                        with st.expander(f"✅ {len(detected_fields)} campi rilevati dal file", expanded=False):
                            df_preview = pd.DataFrame([
                                {"Campo": k, "Valore": f"€ {float(v):,.0f}"}
                                for k, v in detected_fields.items()
                            ])
                            st.dataframe(df_preview, use_container_width=True, hide_index=True)

                    # Nome azienda da file o input
                    file_company = parsed.get("company_name", "")
                    cn = st.text_input(
                        "🏢 Nome Azienda",
                        value=file_company or company_name or "",
                        key="cf_upload_company"
                    )

                    st.success("✅ File analizzato! Risultati Cash Flow qui sotto:")
                    st.divider()

                    # Prepara dati per il motore cashflow
                    # Calcola campi derivati se mancanti
                    def _num(key, default=0):
                        """Legge un valore numerico dal parsed dict, ritorna float sicuro."""
                        v = parsed.get(key, default)
                        try:
                            return float(v)
                        except (TypeError, ValueError):
                            return float(default)

                    dep = _num("depreciation")
                    ca  = _num("current_assets")
                    cl  = _num("current_liabilities")
                    td  = _num("total_debt")

                    data_upload = dict(
                        revenue=_num("revenue"),
                        ebit=_num("ebit"),
                        ebitda=_num("ebitda"),
                        net_income=_num("net_income"),
                        depreciation=dep,
                        interest_expense=_num("interest_expense"),
                        tax_expense=_num("tax_expense"),
                        total_assets=_num("total_assets"),
                        equity=_num("equity"),
                        total_debt=td,
                        current_assets=ca,
                        current_liabilities=cl,
                        accounts_receivable=_num("accounts_receivable"),
                        accounts_payable=_num("accounts_payable"),
                        inventory=_num("inventory"),
                        capex=_num("capex", dep * 1.1 if dep else 0),
                        dividends=_num("dividends"),
                        debt_issued=_num("debt_issued"),
                        debt_repaid=_num("debt_repaid", td * 0.1 if td else 0),
                        prev_current_assets=_num("prev_current_assets", ca * 0.95 if ca else 0),
                        prev_current_liabilities=_num("prev_current_liabilities", cl * 0.95 if cl else 0),
                        prev_fixed_assets=_num("prev_fixed_assets"),
                    )

                    _run_cashflow(data_upload, cn)

                except Exception as e:
                    st.error(f"❌ Errore durante l'analisi: {e}")
                    st.info("💡 Controlla il formato del file o usa il Form Manuale.")

        else:
            # Stato vuoto — guida visiva
            st.markdown("---")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("""
**📊 CSV / Excel**
- 2 o 3 colonne
- Nomi campi standard
- Qualsiasi valuta
                """)
            with col_b:
                st.markdown("""
**📄 PDF Bilancio**
- Estratto automatico
- Formato XBRL/IFRS
- Dati rilevati con AI
                """)
            with col_c:
                st.markdown("""
**⚡ Risultati istantanei**
- Waterfall CF
- Proiezioni 5 anni
- Covenant bancari
                """)

            st.info("⬆️ Carica il file per avviare l'analisi, oppure usa il tab **📝 Form Manuale** per inserire i dati a mano.")

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — FORM MANUALE (contenuto originale)
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_form:
        st.markdown("### 📝 Inserimento Manuale Dati")

        with st.expander("📋 Inserisci / Modifica dati", expanded=True):
            company_name_form = st.text_input("Nome Azienda", value=company_name or "", key="cf_company")

            c1, c2, c3 = st.columns(3)
            def n(label, key, default=0.0):
                d = float(erp_data.get(key, default))
                return st.number_input(label, value=d, format="%.2f", key=f"cf_{key}")

            with c1:
                st.markdown("**📊 Conto Economico**")
                revenue = n("Ricavi", "revenue")
                ebit = n("EBIT", "ebit")
                ebitda = n("EBITDA", "ebitda")
                net_income = n("Utile Netto", "net_income")
                depreciation = n("Ammortamenti", "depreciation")
                interest_expense = n("Oneri Finanziari", "interest_expense")
                tax_expense = n("Imposte", "tax_expense")

            with c2:
                st.markdown("**📋 Stato Patrimoniale**")
                total_assets = n("Totale Attivo", "total_assets")
                equity = n("Patrimonio Netto", "equity")
                total_debt = n("Debiti Finanziari", "total_debt")
                current_assets = n("Attivo Corrente", "current_assets")
                current_liabilities = n("Passivo Corrente", "current_liabilities")
                accounts_receivable = n("Crediti Commerciali", "accounts_receivable")
                accounts_payable = n("Debiti Commerciali", "accounts_payable")
                inventory = n("Magazzino", "inventory")

            with c3:
                st.markdown("**📈 Dati Aggiuntivi**")
                capex = st.number_input("CapEx (Investimenti)", value=float(erp_data.get("capex", depreciation * 1.1 if depreciation else 0)), format="%.2f", key="cf_capex")
                dividends = st.number_input("Dividendi distribuiti", value=0.0, format="%.2f", key="cf_div")
                debt_issued = st.number_input("Nuovi Debiti Emessi", value=0.0, format="%.2f", key="cf_debtissued")
                debt_repaid = st.number_input("Debiti Rimborsati", value=float(total_debt * 0.1) if total_debt else 0.0, format="%.2f", key="cf_debtrepaid")
                prev_ca = st.number_input("Attivo Corrente Anno Prec.", value=float(current_assets * 0.95) if current_assets else 0.0, format="%.2f", key="cf_pca")
                prev_cl = st.number_input("Passivo Corrente Anno Prec.", value=float(current_liabilities * 0.95) if current_liabilities else 0.0, format="%.2f", key="cf_pcl")
                prev_fa = st.number_input("Immobilizzazioni Anno Prec.", value=0.0, format="%.2f", key="cf_pfa")

        data_form = dict(
            revenue=revenue, ebit=ebit, ebitda=ebitda, net_income=net_income,
            depreciation=depreciation, interest_expense=interest_expense,
            tax_expense=tax_expense, total_assets=total_assets, equity=equity,
            total_debt=total_debt, current_assets=current_assets,
            current_liabilities=current_liabilities,
            accounts_receivable=accounts_receivable, accounts_payable=accounts_payable,
            inventory=inventory, capex=capex, dividends=dividends,
            debt_issued=debt_issued, debt_repaid=debt_repaid,
            prev_current_assets=prev_ca, prev_current_liabilities=prev_cl,
            prev_fixed_assets=prev_fa,
        )

        _run_cashflow(data_form, company_name_form)
