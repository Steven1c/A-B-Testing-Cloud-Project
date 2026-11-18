"""
db.py
Modul integrasi database Supabase PostgreSQL (Managed DBaaS).
Mematuhi Interface Contract v1.1 dan mendukung fallback in-memory mock.
"""

import os
import sys
import uuid
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv

from src.contract import ITEM_COLUMNS, PRIMARY_ITEM
from src.errors import (
    DuplicateSessionError,
    DatabaseUnavailableError,
    InvalidScoreError,
    InvalidVariantError,
    IncompleteResponseError,
)

# Muat environment variable dari .env jika ada
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_supabase_client = None

# Mock database lokal untuk pengujian / bila kredensial belum ada (disimpan di sys agar tahan reload)
if not hasattr(sys, "_MOCK_SURVEY_STORAGE"):
    sys._MOCK_SURVEY_STORAGE = {}
_MOCK_STORAGE: Dict[str, dict] = sys._MOCK_SURVEY_STORAGE


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
    answers: Any,
    **kwargs: Any
) -> str:
    """
    Menyimpan 1 respon survei ke database Supabase (atau mock storage lokal).
    Mengembalikan response_id (string UUID).

    Validasi:
    - variant harus 'A' atau 'B' (InvalidVariantError).
    - seluruh 20 butir di ITEM_COLUMNS wajib diisi (IncompleteResponseError).
    - seluruh skor butir harus integer 1 sampai 5 (InvalidScoreError).
    - session_id harus unik (DuplicateSessionError).
    """
    if variant not in ("A", "B"):
        raise InvalidVariantError(f"Varian tidak valid: '{variant}'. Harus 'A' atau 'B'.")

    # Parsing format input jawaban (dict lengkap vs integer tunggal + kwargs)
    full_answers: Dict[str, int] = {}
    if isinstance(answers, dict):
        full_answers = dict(answers)
        missing = [c for c in ITEM_COLUMNS if c not in full_answers]
        if missing:
            raise IncompleteResponseError(
                f"Jawaban belum lengkap. Butir yang belum diisi: {missing}"
            )
    elif isinstance(answers, (int, float)) and not isinstance(answers, bool):
        val = int(answers)
        if not (1 <= val <= 5):
            raise InvalidScoreError(f"Skor tidak valid: '{answers}'. Harus integer antara 1 sampai 5.")
        full_answers = {c: val for c in ITEM_COLUMNS}
        for k, v in kwargs.items():
            if k in ITEM_COLUMNS and v is not None:
                full_answers[k] = int(v)
    else:
        raise InvalidScoreError(f"Format jawaban tidak valid: {answers}")

    # Validasi rentang nilai tiap skor (harus integer 1-5)
    for c in ITEM_COLUMNS:
        val = full_answers[c]
        if not isinstance(val, (int, float)) or isinstance(val, bool) or int(val) != val or not (1 <= int(val) <= 5):
            raise InvalidScoreError(
                f"Skor untuk butir '{c}' tidak valid: '{val}'. Harus integer antara 1 sampai 5."
            )
        full_answers[c] = int(val)

    score = full_answers[PRIMARY_ITEM]
    response_id = str(uuid.uuid4())

    record = {
        "response_id": response_id,
        "session_id": str(session_id),
        "variant": variant,
        "variant_group": variant,
        "score": score,
    }
    for c in ITEM_COLUMNS:
        record[c] = full_answers[c]

    # Sertakan metadata tambahan jika ada
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
    Mengambil seluruh skor metrik utama (PRIMARY_ITEM / sat_overall) untuk uji statistik.
    Format output: {"A": [list skor A], "B": [list skor B]}
    """
    client = get_supabase()
    if client is None:
        scores_a = [
            int(r.get(PRIMARY_ITEM, r.get("score")))
            for r in _MOCK_STORAGE.values()
            if r.get("variant_group", r.get("variant")) == "A"
            and r.get(PRIMARY_ITEM, r.get("score")) is not None
        ]
        scores_b = [
            int(r.get(PRIMARY_ITEM, r.get("score")))
            for r in _MOCK_STORAGE.values()
            if r.get("variant_group", r.get("variant")) == "B"
            and r.get(PRIMARY_ITEM, r.get("score")) is not None
        ]
        return {"A": scores_a, "B": scores_b}

    try:
        res = client.table("survey_responses").select("*").execute()
        data = res.data or []
        scores_a = [
            int(r[PRIMARY_ITEM]) if PRIMARY_ITEM in r and r[PRIMARY_ITEM] is not None else int(r["score"])
            for r in data
            if r.get("variant_group", r.get("variant")) == "A"
            and (r.get(PRIMARY_ITEM) is not None or r.get("score") is not None)
        ]
        scores_b = [
            int(r[PRIMARY_ITEM]) if PRIMARY_ITEM in r and r[PRIMARY_ITEM] is not None else int(r["score"])
            for r in data
            if r.get("variant_group", r.get("variant")) == "B"
            and (r.get(PRIMARY_ITEM) is not None or r.get("score") is not None)
        ]
        return {"A": scores_a, "B": scores_b}
    except Exception as e:
        print(f"Error fetching scores: {e}")
        return {"A": [], "B": []}


def fetch_all_item_scores() -> Dict[str, Dict[str, List[int]]]:
    """
    Mengambil skor seluruh 20 butir dikelompokkan per varian untuk statistik deskriptif.
    Format output: {item_col: {"A": [skor...], "B": [skor...]}}
    """
    result: Dict[str, Dict[str, List[int]]] = {
        col: {"A": [], "B": []} for col in ITEM_COLUMNS
    }

    client = get_supabase()
    if client is None:
        for r in _MOCK_STORAGE.values():
            grp = r.get("variant_group", r.get("variant"))
            if grp in ("A", "B"):
                for col in ITEM_COLUMNS:
                    val = r.get(col)
                    if val is not None:
                        result[col][grp].append(int(val))
        return result

    try:
        res = client.table("survey_responses").select("*").execute()
        data = res.data or []
        for r in data:
            grp = r.get("variant_group", r.get("variant"))
            if grp in ("A", "B"):
                for col in ITEM_COLUMNS:
                    val = r.get(col)
                    if val is not None:
                        result[col][grp].append(int(val))
        return result
    except Exception as e:
        print(f"Error fetching all item scores: {e}")
        return result


def fetch_all_responses() -> pd.DataFrame:
    """Mengambil seluruh data respons sebagai Pandas DataFrame."""
    client = get_supabase()
    if client is None:
        if not _MOCK_STORAGE:
            cols = ["response_id", "session_id", "variant_group", *ITEM_COLUMNS]
            return pd.DataFrame(columns=cols)
        return pd.DataFrame(list(_MOCK_STORAGE.values()))

    try:
        response = client.table("survey_responses").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            for c in ITEM_COLUMNS:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching all responses: {e}")
        return pd.DataFrame()


def reset_database() -> int:
    """
    Mereset data respons survei (baik di mock storage lokal maupun di Supabase).
    Mengembalikan perkiraan jumlah baris yang dihapus.
    """
    global _MOCK_STORAGE
    deleted = len(_MOCK_STORAGE)
    _MOCK_STORAGE.clear()

    client = get_supabase()
    if client is not None:
        try:
            res = client.table("survey_responses").delete().neq("session_id", "").execute()
            if hasattr(res, "data") and res.data:
                deleted = len(res.data)
        except Exception as e:
            print(f"Peringatan: Gagal mereset database Supabase: {e}")
    return deleted


def reset_mock_db() -> None:
    """Mengosongkan mock database lokal (khusus unit test)."""
    reset_database()
