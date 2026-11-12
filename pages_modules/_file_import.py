"""Shared, repeatable CSV/Excel reading for page-specific field mappings."""

from utils.financial_import import read_financial_data
import streamlit as st
from numbers import Real
import pandas as pd


def show_import_preview(data):
    """Preview extracted values without presenting an incomplete risk assessment."""
    show_import_warnings(data)
    period = data.get("_source_period")
    if period:
        st.caption(f"Periodo importato: {period}")
    rows = [{"Campo estratto": key, "Valore": value}
            for key, value in data.items()
            if not key.startswith("_") and isinstance(value, Real) and not isinstance(value, bool)]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.warning("Prospetto importato parzialmente: completa i dati mancanti nella sezione manuale "
               "prima di calcolare indicatori di rischio, liquidità o DSCR. "
               "I dati mancanti non sono valori pari a zero.")


def show_import_warnings(data):
    """Keep source limitations visible at every financial upload entry point."""
    for warning in data.get("_import_warnings", []):
        st.warning(str(warning))


def read_financial_upload(uploaded_file):
    """Read from the start on every rerun; preserve the caller's stream position."""
    data = read_financial_data(uploaded_file)
    show_import_warnings(data)
    return data
