import streamlit as st
import pandas as pd
import numpy as np
from analysis import detect_anomalies, get_stats
from auth import login, register
from db import get_credits, use_credit

# --------------------
# CONFIG
# --------------------
st.set_page_config("COIN-NEXUS SAAS", layout="wide")

# --------------------
# SESSION
# --------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

# --------------------
# LOGIN PAGE
# --------------------
if not st.session_state["user"]:
    st.title("💠 COIN-NEXUS SAAS")

    page = st.radio("Accesso", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if page == "Register":
        if st.button("Crea Account"):
            if register(email, password):
                st.success("Account creato")
            else:
                st.error("Utente già esistente")

    if page == "Login":
        if st.button("Accedi"):
            user = login(email, password)
            if user:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Credenziali errate")

    st.stop()

# --------------------
# USER INFO
# --------------------
user = st.session_state["user"]
email = user["email"]

st.sidebar.title("💠 COIN-NEXUS")
st.sidebar.write(f"👤 {email}")

credits = get_credits(email)
st.sidebar.write(f"💰 Crediti: {credits}")

if st.sidebar.button("Logout"):
    st.session_state["user"] = None
    st.rerun()

# --------------------
# NAVIGATION (PAGINE)
# --------------------
page = st.sidebar.radio("Menu", [
    "Dashboard",
    "Upload & Analysis",
    "Account"
])

# --------------------
# DASHBOARD
# --------------------
if page == "Dashboard":
    st.title("📊 Dashboard")

    st.info("Benvenuto nella tua piattaforma AI di audit forense.")

# --------------------
# ANALYSIS PAGE
# --------------------
elif page == "Upload & Analysis":
    st.title("🧠 AI Analysis")

    uploaded = st.file_uploader("Carica file Excel/CSV")

    if uploaded:
        if not use_credit(email):
            st.error("❌ Crediti terminati")
            st.stop()

        df = pd.read_excel(uploaded) if uploaded.name.endswith("xlsx") else pd.read_csv(uploaded)

        num_col = df.select_dtypes(include=np.number).columns[0]

        st.subheader("Preview")
        st.dataframe(df.head())

        outliers, hhi = get_stats(df, num_col)
        anomalies = detect_anomalies(df, num_col)

        st.metric("Anomalie AI", len(anomalies))
        st.metric("HHI", f"{hhi:.3f}")

        st.subheader("Anomalie trovate")
        st.dataframe(anomalies)

# --------------------
# ACCOUNT PAGE
# --------------------
elif page == "Account":
    st.title("👤 Account")

    st.write(f"Email: {email}")
    st.write(f"Crediti disponibili: {credits}")

    st.info("Upgrade piano per ottenere più analisi")
