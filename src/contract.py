"""
contract.py
Konstanta dan kontrak data bersama antar-layer (Analysis Layer & Infrastructure/App Layer).
Mematuhi Interface Contract v1.1 dan instrumen survei 20 butir.
"""

PRIMARY_ITEM: str = "sat_overall"
MIN_N: int = 10
TARGET_N: int = 64
TARGET_TOTAL_N: int = 128

ITEM_COLUMNS: tuple[str, ...] = (
    # Dimensi 1: Kepuasan & Efektivitas Keseluruhan
    "sat_overall",
    "sat_expectation",
    "sat_effectiveness",
    "sat_preference",
    # Dimensi 2: Pedagogis & Pemahaman Materi
    "mat_comprehension",
    "mat_clarity",
    "mat_retention",
    "mat_readiness",
    # Dimensi 3: Interaksi & Keterlibatan Belajar
    "int_lecturer",
    "int_feedback",
    "int_peers",
    "int_focus",
    # Dimensi 4: Fleksibilitas & Kenyamanan Lingkungan
    "flx_time",
    "flx_location",
    "flx_comfort",
    "flx_pace",
    # Dimensi 5: Dukungan Teknis & Kelancaran Operasional
    "tec_access",
    "tec_stability",
    "tec_submission",
    "tec_attendance",
)
