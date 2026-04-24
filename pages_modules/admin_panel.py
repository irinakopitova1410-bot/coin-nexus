"""
NEXUS Finance Pro — Admin Panel
Gestione completa utenti/clienti via Supabase Edge Function.
"""
import streamlit as st
import requests
import pandas as pd
from services.auth import is_admin, get_supabase, get_supabase_url

EDGE_FN_URL = "https://ipmttldwfsxuubugiyir.supabase.co/functions/v1/create-user"


def _get_token() -> str:
    """Ritorna il JWT dell'admin loggato."""
    user = st.session_state.get("user", {})
    return user.get("access_token", "")


def _call_edge(action: str, body: dict) -> dict:
    """Chiama l'Edge Function create-user con l'azione specificata."""
    token = _get_token()
    if not token:
        return {"error": "Sessione scaduta — rieffettua il login"}
    try:
        r = requests.post(
            f"{EDGE_FN_URL}?action={action}",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def show_admin_panel():
    if not is_admin():
        st.error("⛔ Accesso negato — solo per amministratori")
        return

    st.title("👑 Pannello Amministratore")
    st.caption("Gestisci clienti, utenti e statistiche della piattaforma")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Clienti", "➕ Crea Cliente", "🔑 Reset Password", "📊 Statistiche"])

    # ─────────────────────────────────────────────
    # TAB 1 — Lista Clienti
    # ─────────────────────────────────────────────
    with tab1:
        st.subheader("👥 Clienti Registrati")

        if st.button("🔄 Aggiorna lista", key="refresh_users"):
            st.session_state.pop("cached_users", None)

        if "cached_users" not in st.session_state:
            with st.spinner("Carico utenti..."):
                result = _call_edge("list", {})
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                    st.stop()
                st.session_state["cached_users"] = result.get("users", [])

        users = st.session_state.get("cached_users", [])

        if not users:
            st.info("Nessun utente ancora registrato.")
        else:
            # Filtro ricerca
            search = st.text_input("🔍 Cerca per email o azienda...", key="user_search")
            filtered = [
                u for u in users
                if not search or
                   search.lower() in (u.get("email") or "").lower() or
                   search.lower() in (u.get("company_name") or "").lower()
            ]

            st.markdown(f"**{len(filtered)} utenti trovati**")
            st.markdown("")

            for u in filtered:
                uid = u.get("id", "")
                email = u.get("email", "—")
                name = u.get("full_name") or "—"
                company = u.get("company_name") or "—"
                role = u.get("role", "client")
                active = u.get("is_active", True)
                created = (u.get("created_at") or "")[:10]
                last_login = (u.get("last_sign_in_at") or "Mai")[:10]

                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1.5, 1, 1.5])

                    with col1:
                        badge = "👑" if role == "admin" else "🏢"
                        st.markdown(f"**{badge} {email}**")
                        st.caption(f"{name} · {company}")

                    with col2:
                        st.markdown(f"📅 Creato: `{created}`")
                        st.caption(f"Ultimo login: {last_login}")

                    with col3:
                        st.markdown("✅ Attivo" if active else "❌ Disattivato")

                    with col4:
                        # Toggle attivo/disattivo (non per admin)
                        if role != "admin":
                            label = "🚫 Disattiva" if active else "✅ Attiva"
                            if st.button(label, key=f"toggle_{uid}", use_container_width=True):
                                res = _call_edge("toggle", {"user_id": uid, "is_active": not active})
                                if res.get("success"):
                                    st.success("Aggiornato!")
                                    st.session_state.pop("cached_users", None)
                                    st.rerun()
                                else:
                                    st.error(res.get("error", "Errore"))

                    with col5:
                        if role != "admin":
                            if st.button("🗑️ Elimina", key=f"del_{uid}", use_container_width=True):
                                st.session_state[f"confirm_del_{uid}"] = True

                    # Conferma eliminazione
                    if st.session_state.get(f"confirm_del_{uid}"):
                        st.warning(f"⚠️ Sei sicura di voler eliminare **{email}**? Questa azione è irreversibile.")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Sì, elimina", key=f"yes_del_{uid}"):
                            res = _call_edge("delete", {"user_id": uid})
                            if res.get("success"):
                                st.success(f"Utente {email} eliminato.")
                                st.session_state.pop("cached_users", None)
                                st.session_state.pop(f"confirm_del_{uid}", None)
                                st.rerun()
                            else:
                                st.error(res.get("error", "Errore"))
                        if c2.button("❌ Annulla", key=f"no_del_{uid}"):
                            st.session_state.pop(f"confirm_del_{uid}", None)
                            st.rerun()

                st.divider()

    # ─────────────────────────────────────────────
    # TAB 2 — Crea Nuovo Cliente
    # ─────────────────────────────────────────────
    with tab2:
        st.subheader("➕ Crea Nuovo Cliente")
        st.markdown("Il cliente potrà subito accedere con le credenziali che imposti tu.")
        st.markdown("")

        with st.form("create_client_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_email = st.text_input("📧 Email *", placeholder="cliente@azienda.it")
                new_name = st.text_input("👤 Nome Completo", placeholder="Mario Rossi")
            with col2:
                new_company = st.text_input("🏢 Nome Azienda", placeholder="Rossi Srl")
                new_role = st.selectbox("🎭 Ruolo", ["client", "admin"], help="'client' = vede solo i propri dati")

            st.markdown("")
            new_password = st.text_input(
                "🔑 Password Temporanea *",
                type="password",
                placeholder="min. 8 caratteri",
                help="Il cliente potrà cambiarla dopo il primo accesso"
            )

            st.markdown("")
            submitted = st.form_submit_button("✅ Crea Cliente", use_container_width=True, type="primary")

        if submitted:
            if not new_email or not new_password:
                st.error("❌ Email e password sono obbligatorie")
            elif len(new_password) < 8:
                st.error("❌ La password deve essere di almeno 8 caratteri")
            else:
                with st.spinner("Creazione in corso..."):
                    res = _call_edge("create", {
                        "email": new_email,
                        "password": new_password,
                        "full_name": new_name,
                        "company_name": new_company,
                        "role": new_role
                    })

                if res.get("success"):
                    st.success(f"✅ Cliente **{new_email}** creato con successo!")
                    st.session_state.pop("cached_users", None)

                    st.markdown("---")
                    st.markdown("### 📋 Credenziali da inviare al cliente")
                    st.code(f"""
URL App:  https://nexus-finance-analyzer.streamlit.app/
Email:    {new_email}
Password: {new_password}
                    """, language="text")

                    st.info("💡 Copia e invia queste credenziali al cliente via email o messaggio.")
                else:
                    err = res.get("error", "Errore sconosciuto")
                    st.error(f"❌ {err}")
                    if "already registered" in err.lower() or "already exists" in err.lower():
                        st.info("💡 Questo indirizzo email è già registrato. Prova con un'altra email.")

    # ─────────────────────────────────────────────
    # TAB 3 — Reset Password
    # ─────────────────────────────────────────────
    with tab3:
        st.subheader("🔑 Reset Password Cliente")
        st.markdown("Reimposta la password di un cliente senza che lui debba fare nulla.")
        st.markdown("")

        # Lista email per selezione
        if "cached_users" in st.session_state:
            users_for_reset = [
                u for u in st.session_state["cached_users"]
                if u.get("role") != "admin"
            ]
            emails = [u.get("email", "") for u in users_for_reset]
        else:
            emails = []

        if not emails:
            st.info("Carica prima la lista clienti dal tab 👥 Clienti.")
        else:
            with st.form("reset_pwd_form", clear_on_submit=True):
                selected_email = st.selectbox("📧 Seleziona cliente", emails)
                new_pwd = st.text_input("🔑 Nuova Password *", type="password", placeholder="min. 8 caratteri")
                new_pwd2 = st.text_input("🔑 Conferma Password *", type="password")
                reset_submitted = st.form_submit_button("🔄 Reimposta Password", use_container_width=True, type="primary")

            if reset_submitted:
                if not new_pwd:
                    st.error("❌ Inserisci la nuova password")
                elif new_pwd != new_pwd2:
                    st.error("❌ Le password non coincidono")
                elif len(new_pwd) < 8:
                    st.error("❌ La password deve essere di almeno 8 caratteri")
                else:
                    # Trova user_id dall'email
                    user_id = next(
                        (u["id"] for u in users_for_reset if u.get("email") == selected_email),
                        None
                    )
                    if not user_id:
                        st.error("Utente non trovato")
                    else:
                        with st.spinner("Reset in corso..."):
                            res = _call_edge("reset_password", {
                                "user_id": user_id,
                                "new_password": new_pwd
                            })
                        if res.get("success"):
                            st.success(f"✅ Password di **{selected_email}** reimpostata!")
                            st.code(f"""
Email:    {selected_email}
Password: {new_pwd}
                            """, language="text")
                        else:
                            st.error(f"❌ {res.get('error', 'Errore')}")

    # ─────────────────────────────────────────────
    # TAB 4 — Statistiche Piattaforma
    # ─────────────────────────────────────────────
    with tab4:
        st.subheader("📊 Statistiche Piattaforma")

        supabase = get_supabase()
        try:
            # Conteggi
            users_res = supabase.table("user_profiles").select("id, role").execute()
            all_users = users_res.data or []
            n_clients = sum(1 for u in all_users if u.get("role") == "client")
            n_admins = sum(1 for u in all_users if u.get("role") == "admin")

            analyses_res = supabase.table("analisi_rischio").select("id", count="exact").execute()
            credits_res = supabase.table("credit_analyses").select("id", count="exact").execute()
            audit_res = supabase.table("audit_reports").select("id", count="exact").execute()

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("👥 Clienti", n_clients)
            col2.metric("👑 Admin", n_admins)
            col3.metric("📊 Analisi Rischio", analyses_res.count or 0)
            col4.metric("💳 Credit Scoring", credits_res.count or 0)
            col5.metric("🔍 Audit Report", audit_res.count or 0)

            st.markdown("---")

            # Ultime analisi
            st.markdown("#### 🕐 Ultime analisi effettuate")
            try:
                recent = supabase.table("analisi_rischio").select(
                    "nome_azienda, zscore, rating, created_at"
                ).order("created_at", desc=True).limit(10).execute()

                if recent.data:
                    df = pd.DataFrame(recent.data)
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
                    df.columns = ["Azienda", "Z-Score", "Rating", "Data"]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Nessuna analisi ancora effettuata.")
            except Exception:
                st.info("Dati non disponibili.")

        except Exception as e:
            st.error(f"Errore statistiche: {e}")
