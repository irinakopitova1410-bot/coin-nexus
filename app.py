import streamlit as st
import plotly.graph_objects as go
from supabase import create_client
import pandas as pd

from engine.scoring import calculate_metrics
from services.decision import get_credit_approval


# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Coin-Nexus Credit Intelligence",
    layout="wide"
)

st.title("🏛️ Coin-Nexus | Credit Intelligence Platform")


# ---------------- SUPABASE ----------------
@st.cache_resource
def init_connection():
    return create_client(
        st.secrets["https://ipmttldwfsxuubugiyir.supabase.co"],
        st.secrets["sb_publishable_HasWDK8G-d09qqpGEA-syw_sCPBhpos"]
    )

supabase = init_connection()


# ---------------- DB ----------------
def push_to_db(name, metrics, decision):
    try:
        res = supabase.table("tenants") \
            .select("id") \
            .eq("name", "Doc Finance Partner") \
            .execute()

        if not res.data:
            res = supabase.table("tenants").insert({
                "name": "Doc Finance Partner",
                "api_key": "test"
            }).execute()

        t_id = res.data[0]["id"]

        comp = supabase.table("companies").upsert({
            "company_name": name,
            "tenant_id": t_id
        }, on_conflict="company_name").execute()

        c_id = comp.data[0]["id"]

        supabase.table("credit_analyses").insert({
            "company_id": c_id,
            "dscr_value": metrics["dscr"],
            "leverage_value": metrics["leverage"],
            "rating_code": decision["rating"],
            "decision_output": decision["decision"]
        }).execute()

        return True

    except Exception as e:
        st.error(f"DB error: {e}")
        return False


# ---------------- UI ----------------
tab1, tab2 = st.tabs(["📊 Credit Analysis", "📜 History"])


# ================= TAB 1 =================
with tab1:

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📥 Input Financial Data")

        name = st.text_input("Company Name", "Target S.p.A.")

        revenue = st.number_input("Revenue (€)", value=1_500_000)
        ebitda = st.number_input("EBITDA (€)", value=300_000)
        debt = st.number_input("Total Debt (€)", value=400_000)

        short_debt = st.number_input("Short-term Debt (€)", value=150_000)
        cash = st.number_input("Cash (€)", value=100_000)
        receivables = st.number_input("Receivables (€)", value=200_000)

        run = st.button("🚀 RUN CREDIT ANALYSIS")


    with col2:

        if run:

            # ---------------- METRICS ----------------
            metrics = calculate_metrics({
                "revenue": revenue,
                "ebitda": ebitda,
                "debt": debt,
                "short_debt": short_debt,
                "cash": cash,
                "receivables": receivables
            })

            decision = get_credit_approval(metrics)

            st.session_state["result"] = (metrics, decision, name)

            push_to_db(name, metrics, decision)

        # ---------------- OUTPUT ----------------
        if "result" in st.session_state:

            metrics, d, n = st.session_state["result"]

            st.markdown(f"## 🏢 {n}")

            # SCORE BLOCK
            st.markdown(f"## 🏆 Rating: {d['rating']}")
            st.markdown(f"### {d['decision']}")

            if d["decision"] == "APPROVATO":
                st.success("High probability of credit approval")
            elif d["decision"] == "REVISIONE MANUALE":
                st.warning("Requires manual review")
            else:
                st.error("Low probability of credit approval")

            # FINANCIAL RESULT
            st.markdown("## 💰 Estimated Credit Capacity")
            st.markdown(f"### € {d.get('estimated_credit', 0):,.0f}")

            # GAUGE DSCR
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics["dscr"],
                title={"text": "DSCR (Debt Service Coverage Ratio)"},
                gauge={
                    "axis": {"range": [0, 5]},
                    "bar": {"color": d["color"]}
                }
            ))

            st.plotly_chart(fig, use_container_width=True)

            # METRICS
            st.markdown("## 📊 Key Metrics")

            st.write({
                "DSCR": metrics["dscr"],
                "Leverage": metrics["leverage"],
                "Margin": metrics["margin"],
                "Current Ratio": metrics.get("current_ratio", None)
            })

            # ISSUES
            if d.get("issues"):
                st.markdown("## ⚠️ Risk Factors")
                for i in d["issues"]:
                    st.write(f"- {i}")

            # SUGGESTIONS
            if d.get("suggestions"):
                st.markdown("## ✅ Improvement Actions")
                for s in d["suggestions"]:
                    st.write(f"- {s}")

            # SIMULATION
            if "simulation" in d:
                st.markdown("## 📈 Scenario Simulation")
                st.info(d["simulation"]["message"])
                st.metric(
                    "Potential Improved Score",
                    d["simulation"]["improved_score"]
                )

            # REPORT
            report = f"""
CREDIT INTELLIGENCE REPORT

Company: {n}

Rating: {d['rating']}
Decision: {d['decision']}

DSCR: {metrics['dscr']}
Leverage: {metrics['leverage']}

Estimated Credit: € {d.get('estimated_credit', 0):,.0f}

Risk Factors:
{', '.join(d.get('issues', []))}

Recommendations:
{', '.join(d.get('suggestions', []))}
"""

            st.download_button(
                "📥 Download Credit Report",
                report,
                file_name=f"Credit_Report_{n}.txt"
            )


# ================= TAB 2 =================
with tab2:

    st.subheader("📜 Credit History")

    if st.button("Refresh History"):

        res = supabase.table("credit_analyses") \
            .select("created_at, rating_code, decision_output, companies(company_name)") \
            .execute()

        if res.data:
            df = pd.json_normalize(res.data)
            st.dataframe(df, use_container_width=True)
