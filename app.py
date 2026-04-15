import streamlit as st

from utils.parser import load_data
from engine.scoring import compute_metrics
from services.decision import credit_decision

st.set_page_config(page_title="Coin-Nexus", layout="wide")

st.title("🏦 Coin-Nexus")

file = st.file_uploader("Upload file", type=["csv", "xlsx"])

if file:

    df = load_data(file)
    metrics = compute_metrics(df)
    decision = credit_decision(metrics)

    st.metric("Score", metrics["score"])
    st.success(decision["status"])
