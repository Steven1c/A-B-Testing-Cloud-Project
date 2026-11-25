"""
simulate_data.py
Modul generator data simulasi survei Monte Carlo untuk pengujian A/B testing
Tingkat Kepuasan Pembelajaran: Luring (Varian A) vs Daring (Varian B).
"""

import uuid
from typing import Optional
import numpy as np
import pandas as pd

from src.contract import ITEM_COLUMNS


def _jitter_probs(rng: np.random.Generator, base: list[float], spread: float = 0.03) -> np.ndarray:
    """Beri sedikit variasi acak pada bobot Likert lalu normalisasi agar total = 1.0."""
    arr = np.asarray(base, dtype=float) + rng.uniform(-spread, spread, size=5)
    arr = np.clip(arr, 0.01, None)
    return arr / arr.sum()


def _build_prob_profiles(rng: np.random.Generator, scenario: str) -> tuple[dict, dict]:
    """Menentukan distribusi probabilitas A & B sesuai skenario simulasi."""
    default_a = {
        "sat": [0.03, 0.07, 0.20, 0.45, 0.25],
        "mat": [0.02, 0.08, 0.20, 0.45, 0.25],
        "int": [0.02, 0.05, 0.18, 0.45, 0.30],
        "flx": [0.08, 0.17, 0.35, 0.28, 0.12],
        "tec": [0.03, 0.07, 0.20, 0.45, 0.25],
    }
    default_b = {
        "sat": [0.08, 0.17, 0.35, 0.28, 0.12],
        "mat": [0.06, 0.14, 0.30, 0.35, 0.15],
        "int": [0.12, 0.23, 0.35, 0.20, 0.10],
        "flx": [0.02, 0.05, 0.13, 0.40, 0.40],
        "tec": [0.07, 0.18, 0.35, 0.28, 0.12],
    }

    if scenario == "significant":
        return default_a, default_b

    chosen = scenario
    if scenario == "random":
        chosen = str(rng.choice(["a_better", "b_better", "null", "borderline"], p=[0.30, 0.20, 0.30, 0.20]))

    mid_base = [0.06, 0.15, 0.35, 0.31, 0.13]
    mid_high_base = [0.04, 0.10, 0.27, 0.40, 0.19]

    if chosen == "a_better":
        pa = {k: _jitter_probs(rng, v) for k, v in default_a.items()}
        pb = {k: _jitter_probs(rng, v) for k, v in default_b.items()}
        return pa, pb
    if chosen == "b_better":
        # Balik keunggulan kepuasan ke Daring (B) dengan sedikit variasi antar dimensi
        pa = {k: _jitter_probs(rng, default_b[k]) for k in default_b}
        pb = {k: _jitter_probs(rng, default_a[k]) for k in default_a}
        return pa, pb
    if chosen == "borderline":
        # Selisih tipis: kadang tolak H0, kadang gagal menolak H0
        if rng.random() < 0.5:
            a_ref, b_ref = mid_high_base, mid_base
        else:
            a_ref, b_ref = mid_base, mid_high_base
        pa = {k: _jitter_probs(rng, a_ref, spread=0.025) for k in default_a}
        pb = {k: _jitter_probs(rng, b_ref, spread=0.025) for k in default_b}
        return pa, pb

    # Default "null": kedua grup berasal dari level populasi yang setara (cenderung gagal menolak H0)
    shared = mid_base if rng.random() < 0.5 else mid_high_base
    pa = {k: _jitter_probs(rng, shared, spread=0.02) for k in default_a}
    pb = {k: _jitter_probs(rng, shared, spread=0.02) for k in default_b}
    return pa, pb


def generate_responses(
    n_a: int = 70,
    n_b: int = 70,
    seed: Optional[int] = 42,
    scenario: str = "significant",
) -> pd.DataFrame:
    """
    Menghasilkan data simulasi responden A/B testing berbasis metode Monte Carlo.
    Mematuhi Interface Contract (docs/interface-contract.md) dan instrumen survei 20 butir.

    Parameter `scenario`:
    - "significant" (default): Varian A unggul jelas di sat_overall (konsisten untuk pengujian deterministik).
    - "random": mengacak skenario (A unggul, B unggul, efek tipis, atau H0 setara) tiap eksekusi.
    - "a_better" | "b_better" | "borderline" | "null": pilih skenario distribusi secara eksplisit.
    """
    rng = np.random.default_rng(seed)
    scores = np.array([1, 2, 3, 4, 5], dtype=int)

    prob_a, prob_b = _build_prob_profiles(rng, scenario)

    dimensions = {
        "sat": [
            "sat_overall",
            "sat_expectation",
            "sat_effectiveness",
            "sat_preference",
        ],
        "mat": [
            "mat_comprehension",
            "mat_clarity",
            "mat_retention",
            "mat_readiness",
        ],
        "int": [
            "int_lecturer",
            "int_feedback",
            "int_peers",
            "int_focus",
        ],
        "flx": [
            "flx_time",
            "flx_location",
            "flx_comfort",
            "flx_pace",
        ],
        "tec": [
            "tec_access",
            "tec_stability",
            "tec_submission",
            "tec_attendance",
        ],
    }

    records = []
    groups = [("A", n_a, prob_a), ("B", n_b, prob_b)]

    for group, n_count, probs in groups:
        for _ in range(n_count):
            sid = f"sim_{uuid.uuid4().hex[:12]}"
            row = {
                "session_id": sid,
                "variant_group": group,
            }

            for dim_key, cols in dimensions.items():
                for col in cols:
                    row[col] = int(rng.choice(scores, p=probs[dim_key]))

            records.append(row)

    target_columns = ["session_id", "variant_group", *ITEM_COLUMNS]
    df = pd.DataFrame(records)[target_columns]
    # Acak urutan baris (aman untuk seed > 2**32 maupun seed=None)
    shuffle_seed = int(rng.integers(0, 2**32 - 1))
    df = df.sample(frac=1.0, random_state=shuffle_seed).reset_index(drop=True)
    return df


def generate_monte_carlo_survey(n_per_group: int = 70, seed: int = 42) -> pd.DataFrame:
    """Alias untuk fungsi generate_responses untuk kompatibilitas notebook / script tim."""
    return generate_responses(n_a=n_per_group, n_b=n_per_group, seed=seed)


if __name__ == "__main__":
    df_sim = generate_responses(n_a=70, n_b=70, seed=42)
    print(f"Berhasil menghasilkan {len(df_sim)} baris data simulasi.")
    print(f"Kolom: {list(df_sim.columns)}")
    print(df_sim[["session_id", "variant", "score"]].head())
    print("\nRingkasan skor per varian:")
    print(df_sim.groupby("variant")["score"].describe())
