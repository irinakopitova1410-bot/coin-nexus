import streamlit as st
import pandas as pd

from utils.parser import load_data
from engine.scoring import compute_metrics, risk_label

st.set_page_config(page_title="Coin-Nexus", layout="wide")

st.title("🏦 Coin-Nexus | Financial Intelligence Engine")

uploaded = st.file_uploader("Carica file ERP", type=["csv", "xlsx"])

if uploaded:

    df = load_data(uploaded)
    st.dataframe(df)

    metrics = compute_metrics(df)

    st.metric("Score", f"{metrics['score']}/100")
    st.success(risk_label(metrics["score"]))

    st.subheader("Explainability")

    for r in metrics["reasons"]:
        st.write("•", r)
