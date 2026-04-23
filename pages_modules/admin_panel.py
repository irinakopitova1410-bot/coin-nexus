import streamlit as st
from services.auth import get_supabase, is_admin

def show_admin_panel():
    if not is_admin():
        st.error("⛔ Accesso negato — solo per amministratori")
        return

    st.title("👑 Pannello Amministratore")
    st.markdown("---")

    supabase = get_supabase()

    tab1, tab2, tab3 = st.tabs(["👥 Utenti", "➕ Crea Utente", "📊 Statistiche"])

    # ─── TAB 1: Lista Utenti ───
    with tab1:
        st.subheader("Utenti Registrati")
        try:
            result = supabase.table("user_profiles").select("*").order("created_at", desc=True).execute()
            users = result.data or []
            if users:
                import pandas as pd
                df = pd.DataFrame(users)[["email", "full_name", "role", "company_name", "is_active", "created_at"]]
                df.columns = ["Email", "Nome", "Ruolo", "Azienda", "Attivo", "Creato il"]
                df["Creato il"] = pd.to_datetime(df["Creato il"]).dt.strftime("%d/%m/%Y")

                for _, row in df.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    col1.write(f"**{row['Email']}**")
                    col2.write(row["Azienda"] or "—")
                    badge = "👑 Admin" if row["Ruolo"] == "admin" else "🏢 Cliente"
                    col3.write(badge)
                    status = "✅" if row["Attivo"] else "❌"
                    col4.write(status)
                    st.divider()
            else:
                st.info("Nessun utente trovato")
        except Exception as e:
            st.error(f"Errore: {e}")

    # ─── TAB 2: Crea Nuovo Utente ───
    with tab2:
        st.subheader("Crea Nuovo Cliente")
        with st.form("new_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_email = st.text_input("📧 Email *")
                new_name = st.text_input("👤 Nome Completo")
            with col2:
                new_company = st.text_input("🏢 Nome Azienda")
                new_role = st.selectbox("🎭 Ruolo", ["client", "admin"])
            new_password = st.text_input("🔑 Password Temporanea *", type="password")
            submitted = st.form_submit_button("✅ Crea Utente", use_container_width=True)

            if submitted:
                if not new_email or not new_password:
                    st.error("Email e password sono obbligatorie")
                else:
                    try:
                        # Crea utente su Supabase Auth
                        result = supabase.auth.admin.create_user({
                            "email": new_email,
                            "password": new_password,
                            "email_confirm": True,
                            "user_metadata": {
                                "full_name": new_name,
                                "role": new_role
                            }
                        })
                        # Aggiorna profilo
                        supabase.table("user_profiles").update({
                            "full_name": new_name,
                            "company_name": new_company,
                            "role": new_role
                        }).eq("id", result.user.id).execute()

                        st.success(f"✅ Utente **{new_email}** creato con successo!")
                        st.info(f"📧 Credenziali da inviare al cliente:\n- Email: `{new_email}`\n- Password: `{new_password}`")
                    except Exception as e:
                        st.error(f"Errore creazione utente: {e}")

    # ─── TAB 3: Statistiche ───
    with tab3:
        st.subheader("Statistiche Piattaforma")
        try:
            users_res = supabase.table("user_profiles").select("role", count="exact").execute()
            analyses_res = supabase.table("analisi_rischio").select("id", count="exact").execute()
            credits_res = supabase.table("credit_analyses").select("id", count="exact").execute()

            col1, col2, col3 = st.columns(3)
            col1.metric("👥 Utenti Totali", len(users_res.data or []))
            col2.metric("📊 Analisi Rischio", analyses_res.count or 0)
            col3.metric("💳 Credit Scoring", credits_res.count or 0)
        except Exception as e:
            st.error(f"Errore statistiche: {e}")
