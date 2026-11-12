"""Shared, repeatable CSV/Excel reading for page-specific field mappings."""

from utils.financial_import import read_financial_data
import streamlit as st
from numbers import Real
import pandas as pd


def show_import_preview(data, include_notes=True):
    """Preview extracted values without presenting an incomplete risk assessment."""
    period = data.get("_source_period")
    st.subheader("Dati letti dal bilancio")
    if period:
        st.caption(f"Periodo importato: {period}")
    labels = {
        "fatturato": "Ricavi", "ricavi_netti": "Ricavi netti", "ebitda": "EBITDA", "ebit": "Risultato operativo (EBIT)",
        "utile_netto": "Utile / perdita netta", "totale_attivo": "Totale attivo",
        "patrimonio_netto": "Patrimonio netto", "attivo_corrente": "Attivo corrente",
        "passivo_corrente": "Passività correnti", "cash_flow_operativo": "Flusso di cassa operativo",
        "disponibilita_liquide": "Disponibilità liquide",
    }
    rows = [{"Voce di bilancio": labels.get(key, key.replace("_", " ").capitalize()),
             "Importo (EUR)": f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}
            for key, value in data.items()
            if not key.startswith("_") and isinstance(value, Real) and not isinstance(value, bool)]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.info("Il file è stato letto. Per completare l’analisi, integra i dati mancanti "
            "nella scheda «Inserisci Manualmente». Un dato assente non equivale a zero.")
    if include_notes:
        show_import_warnings(data)


def show_import_warnings(data):
    """Keep source limitations visible at every financial upload entry point."""
    notes = list(dict.fromkeys(str(note) for note in data.get("_import_warnings", [])))
    if not notes:
        return
    # A reconciliation error remains prominent; explanatory notes do not flood the page.
    for note in notes:
        if note.startswith("ATTENZIONE:"):
            st.warning(note)
    with st.expander(f"Dettagli di lettura e limiti del bilancio ({len(notes)})", expanded=False):
        for note in notes:
            st.write("• " + note)


def read_financial_upload(uploaded_file):
    """Read from the start on every rerun; preserve the caller's stream position."""
    data = read_financial_data(uploaded_file)
    show_import_warnings(data)
    return data
