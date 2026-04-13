
from supabase_client import supabase

def register(email, password):
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if len(existing.data) > 0:
        return False

    supabase.table("users").insert({
        "email": email,
        "password": password,
        "credits": 5
    }).execute()
    return True


def login(email, password):
    res = supabase.table("users").select("*").eq("email", email).execute()
    if len(res.data) == 0:
        return None

    user = res.data[0]
    if user["password"] == password:
        return user
    return None
