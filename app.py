import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime
import sqlite3
import bcrypt
from sklearn.ensemble import IsolationForest

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="COIN-NEXUS QUANTUM AI",
    layout="wide",
    page_icon="💠"
)

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("coin_nexus.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    credits INTEGER
)
""")
conn.commit()

# =========================
# AUTH FUNCTIONS
# =========================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def create_user(email, password):
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (email, hashed, 5))
        conn.commit()
        return True
    except:
        return False

def login_user(email, password):
    c.execute("SELECT password FROM users WHERE email=?", (email,))
    res = c.fetchone()
    if res:
        return check_password(password, res[0])
    return False

def get_credits(email):
    c.execute("SELECT credits FROM users WHERE email=?", (email,))
    row = c.fetchone()
    return row[0] if row else 0

def use_credit(email):
    credits = get_credits(email)
    if credits > 0:
        c.execute("UPDATE users SET credits=? WHERE email=?", (credits - 1, email))
        conn.commit()
        return True
    return False

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state["user"] = None

# =========================
# LOGIN PAGE
# =========================
if not st.session_state["user"]:
    st.title("💠 COIN-NEXUS LOGIN")

    mode = st.radio("Accesso", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Register":
        if st.button("Crea Account"):
            if create_user(email, password):
                st.success("Account creato! Ora fai login.")
            else:
                st.error("Utente già esistente")

    if mode == "Login":
        if st.button("Accedi"):
            if login_user(email, password):
                st.session_state["user"] = email
                st.success("Accesso effettuato")
                st.rerun()
            else:
                st.error("Credenziali errate")

    st.stop()

# =========================
# MAIN APP
# =========================
st.title("💠 COIN-NEXUS QUANTUM AI")
st.caption("Financial AI Risk & Forensic Analytics")

# Sidebar
with st.sidebar:
    st.write(f"👤 {st.session_state['user']}")
    st.write(f"💰 Crediti: {get_credits(st.session_state['user'])}")

    if st.button("LOGOUT"):
        st.session_state["user"] = None
        st.rerun()

# =========================
# FUNCTIONS
# =========================
def detect_ai_anomalies(df, col):
    model = IsolationForest(contamination=0.05, random_state=42)
    df = df.copy()
    df["ai_risk"] = model.fit_predict(df[[col]])
    return df[df["ai_risk"] == -1]

def get_stats(df, col):
    mean = df[col].mean()
    std = df[col].std()
    df["z"] = (df[col] - mean) / std
    outliers = df[df["z"].abs() > 2]
    hhi = ((df[col] / df[col].sum()) ** 2).sum()
    return outliers, hhi

def generate_pdf(massa, mat, anomalies, hhi, studio, note):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, studio, ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Massa: {massa}", ln=True)
    pdf.cell(0, 10, f"Materialita: {mat}", ln=True)
    pdf.cell(0, 10, f"Anomalie AI: {len(anomalies)}", ln=True)
    pdf.cell(0, 10, f"HHI: {hhi:.3f}", ln=True)

    pdf.multi_cell(0, 10, f"Note: {note}")

    return pdf.output(dest="S")

# =========================
# UPLOAD
# =========================
uploaded = st.file_uploader("Carica file Excel/CSV", type=["xlsx", "csv"])

if uploaded:
    # CREDIT CHECK
    if not use_credit(st.session_state["user"]):
        st.error("❌ Crediti terminati")
        st.stop()

    df = pd.read_excel(uploaded) if uploaded.name.endswith("xlsx") else pd.read_csv(uploaded)

    num_col = df.select_dtypes(include=np.number).columns[0]

    massa = df[num_col].sum()
    mat = massa * 0.015

    outliers, hhi = get_stats(df, num_col)
    anomalies = detect_ai_anomalies(df, num_col)

    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Massa", f"€{massa:,.2f}")
    c2.metric("Materialità", f"€{mat:,.2f}")
    c3.metric("Anomalie", len(anomalies))
    c4.metric("HHI", f"{hhi:.3f}")

    # CHART
    st.subheader("Analisi dati")
    st.dataframe(df.head())

    # REPORT
    st.subheader("Report")

    note = st.text_area("Note audit", "Analisi automatizzata Coin Nexus AI")

    if st.button("Genera PDF"):
        pdf = generate_pdf(massa, mat, anomalies, hhi, "COIN-NEXUS", note)
        st.download_button(
            "Scarica Report",
            data=pdf,
            file_name="report.pdf"
        )
