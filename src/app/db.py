"""
db.py
Modul integrasi database Supabase PostgreSQL (Managed DBaaS).
Mematuhi Interface Contract (docs/interface-contract.md) dan mendukung fallback in-memory mock.
"""

import os
import uuid
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv

from src.errors import (
    DuplicateSessionError,
    DatabaseUnavailableError,
    InvalidScoreError,
    InvalidVariantError,
)

# Muat environment variable dari .env jika ada
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client = None

# Mock database lokal untuk pengujian / bila kredensial belum ada
_MOCK_STORAGE: Dict[str, dict] = {}


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


def insert_response(
    session_id: str,
    variant: str,
    score: int,
    **kwargs: Any
) -> str:
    """
    Menyimpan 1 respon survei ke database Supabase (atau mock storage lokal).
    Mengembalikan response_id (string UUID).

    Validasi:
    - variant harus 'A' atau 'B' (InvalidVariantError).
    - score harus integer 1 sampai 5 (InvalidScoreError).
    - session_id harus unik (DuplicateSessionError).
    """
    if variant not in ("A", "B"):
        raise InvalidVariantError(f"Varian tidak valid: '{variant}'. Harus 'A' atau 'B'.")

    if not isinstance(score, (int, float)) or int(score) != score or not (1 <= int(score) <= 5):
        raise InvalidScoreError(f"Skor tidak valid: '{score}'. Harus integer antara 1 sampai 5.")

    score = int(score)
    response_id = str(uuid.uuid4())

    record = {
        "response_id": response_id,
        "session_id": str(session_id),
        "variant": variant,
        "score": score,
        "sat_overall": score,
    }
    # Masukkan kolom diagnostik opsional jika disediakan
    for k, v in kwargs.items():
        if k not in record and v is not None:
            record[k] = v

    client = get_supabase()
    if client is None:
        # Fallback in-memory mock storage
        if session_id in _MOCK_STORAGE:
            raise DuplicateSessionError(f"Session '{session_id}' sudah pernah mengirim respons.")
        _MOCK_STORAGE[session_id] = record
        return response_id

    try:
        # Eksekusi insert ke Supabase
        res = client.table("survey_responses").insert(record).execute()
        if hasattr(res, "data") and res.data and "response_id" in res.data[0]:
            return str(res.data[0]["response_id"])
        return response_id
    except Exception as e:
        err_msg = str(e).lower()
        if "duplicate" in err_msg or "unique" in err_msg or "23505" in err_msg:
            raise DuplicateSessionError(f"Session '{session_id}' sudah pernah mengirim respons.") from e
        raise DatabaseUnavailableError(f"Gagal menghubungi database: {e}") from e


def fetch_scores() -> Dict[str, List[int]]:
    """
    Mengambil seluruh skor metrik utama untuk uji statistik.
    Format output: {"A": [list skor A], "B": [list skor B]}
    """
    client = get_supabase()
    if client is None:
        scores_a = [r["score"] for r in _MOCK_STORAGE.values() if r["variant"] == "A"]
        scores_b = [r["score"] for r in _MOCK_STORAGE.values() if r["variant"] == "B"]
        return {"A": scores_a, "B": scores_b}

    try:
        res = client.table("survey_responses").select("variant, score").execute()
        data = res.data or []
        scores_a = [int(r["score"]) for r in data if r.get("variant") == "A" and r.get("score") is not None]
        scores_b = [int(r["score"]) for r in data if r.get("variant") == "B" and r.get("score") is not None]
        return {"A": scores_a, "B": scores_b}
    except Exception as e:
        print(f"Error fetching scores: {e}")
        return {"A": [], "B": []}


def fetch_all_responses() -> pd.DataFrame:
    """Mengambil seluruh data respons sebagai Pandas DataFrame."""
    client = get_supabase()
    if client is None:
        if not _MOCK_STORAGE:
            return pd.DataFrame(columns=["response_id", "session_id", "variant", "score"])
        return pd.DataFrame(list(_MOCK_STORAGE.values()))

    try:
        response = client.table("survey_responses").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            if "score" in df.columns:
                df["score"] = pd.to_numeric(df["score"], errors="coerce")
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching all responses: {e}")
        return pd.DataFrame()


def reset_mock_db() -> None:
    """Mengosongkan mock database lokal (khusus unit test)."""
    global _MOCK_STORAGE
    _MOCK_STORAGE.clear()
