from supabase import create_client

SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_ANON_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
