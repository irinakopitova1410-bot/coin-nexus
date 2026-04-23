"""
NEXUS Finance Pro — ERP Import Page
Import da SAP, Zucchetti, TeamSystem, Sage, MS Dynamics, CSV generico.
"""
import streamlit as st
import pandas as pd
import io
from services.erp_connectors import (
    parse_erp_file, get_template_df,
    REQUIRED_FIELDS, OPTIONAL_FIELDS, ERP_COLUMN_MAPS
)


def render_erp_import():
    st.title("🔌 Import da ERP / Bilancio")
    st.markdown("""
    Carica direttamente l'export del tuo gestionale. NEXUS riconosce automaticamente
    il formato e mappa i campi senza configurazione manuale.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 Formati supportati")
        erp_list = [
            ("🔷 SAP", "Export standard da SAP FI/CO"),
            ("🟢 Zucchetti", "Export bilancio da Ad Hoc / Infinity"),
            ("🔵 TeamSystem", "Export da Lynfa / Enterprise"),
            ("🟣 Sage", "Export da Sage X3 / 50cloud"),
            ("⚪ MS Dynamics", "Export da Business Central / AX"),
            ("📄 CSV/Excel generico", "Auto-detect dei campi"),
        ]
        for erp, desc in erp_list:
            st.markdown(f"**{erp}** — {desc}")

    with col2:
        st.subheader("📋 Scarica Template")
        tpl_type = st.selectbox("Scegli formato template:",
                                ["GENERIC", "SAP", "ZUCCHETTI", "TEAMSYSTEM", "SAGE", "DYNAMICS"])
        tpl_df = get_template_df(tpl_type)
        csv_buf = io.StringIO()
        tpl_df.to_csv(csv_buf, index=False, sep=";")
        st.download_button(
            "⬇️ Scarica Template CSV",
            data=csv_buf.getvalue().encode("utf-8-sig"),
            file_name=f"template_{tpl_type.lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()

    # ── Upload ────────────────────────────────────────────────────────────────
    st.subheader("📤 Carica il tuo file")

    company_name = st.text_input("Nome azienda (per il report)", value="", placeholder="Es: Rossi S.r.l.")

    uploaded = st.file_uploader(
        "Trascina qui il file oppure clicca per selezionarlo",
        type=["csv", "xlsx", "xls"],
        help="Formati accettati: CSV (separatore ; o ,), Excel .xlsx/.xls"
    )

    if uploaded:
        with st.spinner("⚙️ Analisi del file in corso..."):
            file_bytes = uploaded.read()
            result = parse_erp_file(file_bytes, uploaded.name)

        if not result.success:
            st.error(f"❌ Errore nella lettura del file: {result.error}")
            return

        # Risultato import
        col1, col2, col3 = st.columns(3)
        col1.metric("Formato rilevato", result.erp_type)
        col2.metric("Righe importate", result.rows_imported)
        col3.metric("Campi estratti", len(result.data))

        if result.missing_required:
            st.warning(f"⚠️ Campi obbligatori mancanti: **{', '.join(result.missing_required)}**")
            st.info("Compila manualmente i campi mancanti qui sotto.")
        else:
            st.success("✅ Tutti i campi obbligatori trovati! Dati pronti per l'analisi.")

        # Mostra dati estratti
        with st.expander("👁️ Visualizza dati estratti", expanded=False):
            if result.raw_df is not None:
                st.dataframe(result.raw_df.head(10), use_container_width=True)

        # Editor dati estratti
        st.subheader("✏️ Verifica e correggi i dati")

        all_fields = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}
        edited_data = {}

        cols = st.columns(3)
        for i, (key, label) in enumerate(all_fields.items()):
            val = result.data.get(key, 0.0)
            with cols[i % 3]:
                edited_data[key] = st.number_input(
                    label,
                    value=float(val) if val else 0.0,
                    format="%.2f",
                    key=f"erp_{key}",
                    help=f"Campo: {key}"
                )

        if company_name:
            edited_data["company_name"] = company_name

        # Salva in session state per usare nelle altre pagine
        if st.button("✅ Usa questi dati per l'analisi", type="primary", use_container_width=True):
            st.session_state["erp_data"] = edited_data
            st.session_state["erp_company"] = company_name
            st.success(f"""
            ✅ **Dati salvati!** Ora puoi andare su:
            - 📊 **Analisi Rischio** → Z-Score Altman
            - 📈 **Ratio Analysis** → 35+ indicatori
            - 💰 **Cash Flow** → Rendiconto finanziario
            - 🏅 **Credit Scoring** → Rating creditizio
            """)

        # Mostra anteprima dati chiave
        if result.data:
            st.subheader("📊 Anteprima dati chiave")
            fmt = lambda v: f"€ {v:,.0f}" if v else "—"
            preview = {
                "Totale Attivo": fmt(result.data.get("total_assets")),
                "Ricavi": fmt(result.data.get("revenue")),
                "EBITDA": fmt(result.data.get("ebitda")),
                "EBIT": fmt(result.data.get("ebit")),
                "Patrimonio Netto": fmt(result.data.get("equity")),
                "Utile Netto": fmt(result.data.get("net_income")),
                "Totale Passivo": fmt(result.data.get("total_liabilities")),
                "Attivo Corrente": fmt(result.data.get("current_assets")),
                "Passivo Corrente": fmt(result.data.get("current_liabilities")),
            }
            df_preview = pd.DataFrame(list(preview.items()), columns=["Voce", "Valore"])
            st.dataframe(df_preview, use_container_width=True, hide_index=True)
    else:
        # Mostra istruzioni
        st.info("""
        **Come funziona:**
        1. Esporta il bilancio dal tuo gestionale in formato CSV o Excel
        2. Carica il file qui — NEXUS rileva automaticamente il formato
        3. Verifica i dati estratti e correggi eventuali errori
        4. Clicca "Usa questi dati" per avviare tutte le analisi

        **Suggerimento:** Se non hai un export del gestionale, usa il template CSV
        e compilalo manualmente con i dati del bilancio.
        """)
