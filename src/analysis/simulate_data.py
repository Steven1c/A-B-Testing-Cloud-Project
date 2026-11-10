"""
simulate_data.py
Script simulasi data Monte Carlo untuk mengenerate data responden sintetis
sesuai target sampel Power Analysis (diizinkan oleh ketentuan brief: 'data anonim atau simulasi').
"""

import uuid
import random
import numpy as np
import pandas as pd


def generate_simulated_responses(n_per_variant: int = 130, seed: int = 42) -> pd.DataFrame:
    """
    Menghasilkan data simulasi responden A/B testing:
    - Varian A (Kontrol): Rata-rata minat ~ 5.8, Peluang konversi klik ~ 22%
    - Varian B (Treatment): Rata-rata minat ~ 6.5, Peluang konversi klik ~ 36%
    """
    np.random.seed(seed)
    random.seed(seed)

    rows = []

    # 1. Generate Varian A
    scores_a = np.random.normal(loc=5.8, scale=1.5, size=n_per_variant)
    scores_a = np.clip(np.round(scores_a), 1, 10).astype(int)
    clicks_a = np.random.binomial(n=1, p=0.22, size=n_per_variant)

    for i in range(n_per_variant):
        rows.append({
            "session_id": str(uuid.uuid4())[:8],
            "assigned_variant": "A",
            "willingness_to_pay": int(scores_a[i]),
            "perceived_trust": random.randint(2, 4),
            "clicked_signup": bool(clicks_a[i]),
            "time_spent_sec": round(float(np.random.exponential(scale=18.0) + 5.0), 1)
        })

    # 2. Generate Varian B
    scores_b = np.random.normal(loc=6.6, scale=1.4, size=n_per_variant)
    scores_b = np.clip(np.round(scores_b), 1, 10).astype(int)
    clicks_b = np.random.binomial(n=1, p=0.36, size=n_per_variant)

    for i in range(n_per_variant):
        rows.append({
            "session_id": str(uuid.uuid4())[:8],
            "assigned_variant": "B",
            "willingness_to_pay": int(scores_b[i]),
            "perceived_trust": random.randint(3, 5),
            "clicked_signup": bool(clicks_b[i]),
            "time_spent_sec": round(float(np.random.exponential(scale=24.0) + 8.0), 1)
        })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df_sim = generate_simulated_responses(n_per_variant=130)
    print(f"Berhasil menghasilkan {len(df_sim)} baris data simulasi.")
    print("Contoh 5 baris pertama:")
    print(df_sim.head())
    print("\nRingkasan statistik kesediaan bayar:")
    print(df_sim.groupby("assigned_variant")["willingness_to_pay"].describe())
