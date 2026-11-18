"""
simulate_data.py
Modul generator data simulasi survei Monte Carlo untuk pengujian A/B testing
Tingkat Kepuasan Pembelajaran: Luring (Varian A) vs Daring (Varian B).
"""

import uuid
from typing import Optional
import numpy as np
import pandas as pd


def generate_responses(
    n_a: int = 70,
    n_b: int = 70,
    seed: Optional[int] = 42
) -> pd.DataFrame:
    """
    Menghasilkan data simulasi responden A/B testing berbasis metode Monte Carlo.
    Mematuhi Interface Contract (docs/interface-contract.md) dan instrumen survei 20 butir.

    Output DataFrame memiliki kolom wajib:
    - session_id: ID sesi unik anonim (string)
    - variant: 'A' (Luring) atau 'B' (Daring)
    - score: Skor metrik utama kepuasan (integer 1-5, identik dengan sat_overall)
    Serta 20 kolom diagnostik Likert 1-5 sesuai docs/instrumen survei.md.
    """
    rng = np.random.default_rng(seed)
    scores = np.array([1, 2, 3, 4, 5], dtype=int)

    # Probabilitas distribusi Likert 1-5 untuk masing-masing dimensi
    prob_a = {
        "sat": [0.03, 0.07, 0.20, 0.45, 0.25],
        "mat": [0.02, 0.08, 0.20, 0.45, 0.25],
        "int": [0.02, 0.05, 0.18, 0.45, 0.30],
        "flx": [0.08, 0.17, 0.35, 0.28, 0.12],
        "tec": [0.03, 0.07, 0.20, 0.45, 0.25],
    }

    prob_b = {
        "sat": [0.08, 0.17, 0.35, 0.28, 0.12],
        "mat": [0.06, 0.14, 0.30, 0.35, 0.15],
        "int": [0.12, 0.23, 0.35, 0.20, 0.10],
        "flx": [0.02, 0.05, 0.13, 0.40, 0.40],
        "tec": [0.07, 0.18, 0.35, 0.28, 0.12],
    }

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
                "variant": group,
                "variant_group": group,  # alias untuk kompatibilitas skema
            }

            for dim_key, cols in dimensions.items():
                for col in cols:
                    row[col] = int(rng.choice(scores, p=probs[dim_key]))

            # Metrik utama H0 vs H1 adalah sat_overall (skala 1-5)
            row["score"] = int(row["sat_overall"])
            records.append(row)

    df = pd.DataFrame(records)
    # Acak urutan baris
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
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
