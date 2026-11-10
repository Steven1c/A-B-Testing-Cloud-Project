import os
import pandas as pd
from dotenv import load_dotenv

# Muat environment variable dari .env jika ada
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client = None

def get_supabase():
    """Mengembalikan instance Supabase client. Mengembalikan None jika kredensial belum ada."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY or "your-project" in SUPABASE_URL:
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        print(f"Peringatan: Gagal menginisialisasi Supabase client: {e}")
        return None


def insert_response(data: dict) -> bool:
    """Menyimpan 1 respon survei ke database Supabase."""
    client = get_supabase()
    if client is None:
        # Fallback lokal jika database belum terhubung
        print("[MOCK DB INSERT]", data)
        return True

    try:
        client.table("survey_responses").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error insert database: {e}")
        return False


def fetch_all_responses() -> pd.DataFrame:
    """Mengambil seluruh data respon dari Supabase sebagai Pandas DataFrame."""
    client = get_supabase()
    if client is None:
        # Kembalikan DataFrame kosong jika belum ada koneksi
        return pd.DataFrame(columns=[
            "id", "session_id", "assigned_variant", 
            "willingness_to_pay", "perceived_trust", 
            "clicked_signup", "time_spent_sec", "created_at"
        ])

    try:
        response = client.table("survey_responses").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df["willingness_to_pay"] = pd.to_numeric(df["willingness_to_pay"])
            df["perceived_trust"] = pd.to_numeric(df["perceived_trust"])
            df["clicked_signup"] = df["clicked_signup"].astype(bool)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
