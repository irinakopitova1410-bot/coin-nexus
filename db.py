
from supabase_client import supabase

def get_credits(email):
    res = supabase.table("users").select("credits").eq("email", email).execute()
    return res.data[0]["credits"]

def use_credit(email):
    credits = get_credits(email)

    if credits <= 0:
        return False

    supabase.table("users").update({
        "credits": credits - 1
    }).eq("email", email).execute()

    return True
