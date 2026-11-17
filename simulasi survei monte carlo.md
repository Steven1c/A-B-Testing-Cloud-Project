# Simulasi Data Survei Monte Carlo

 Simulasi survei menggunakan metode **Monte Carlo** dengan skala Likert (1–5) pada dua kelompok varian (`A` dan `B`).

## Kode Python

```
import numpy as np
import pandas as pd

def generate_monte_carlo_survey(n_per_group=70, seed=42):
    rng = np.random.default_rng(seed)
    scores = np.array([1, 2, 3, 4, 5])

    prob_A = {
        "sat": [0.03, 0.07, 0.20, 0.45, 0.25],
        "mat": [0.02, 0.08, 0.20, 0.45, 0.25],
        "int": [0.02, 0.05, 0.18, 0.45, 0.30],
        "flx": [0.08, 0.17, 0.35, 0.28, 0.12],
        "eff": [0.03, 0.07, 0.20, 0.45, 0.25],
    }

    prob_B = {
        "sat": [0.08, 0.17, 0.35, 0.28, 0.12],
        "mat": [0.06, 0.14, 0.30, 0.35, 0.15],
        "int": [0.12, 0.23, 0.35, 0.20, 0.10],
        "flx": [0.02, 0.05, 0.13, 0.40, 0.40],
        "eff": [0.07, 0.18, 0.35, 0.28, 0.12],
    }

    dimensions = {
        "sat": [
            "sat_overall",
            "sat_expectation",
            "sat_recommend",
            "sat_effectiveness",
        ],
        "mat": [
            "mat_comprehension",
            "mat_clarity",
            "mat_retention",
            "mat_readiness",
        ],
        "int": [
            "int_lecturer",
            "int_peers",
            "int_focus",
            "int_engagement",
        ],
        "flx": [
            "flx_time",
            "flx_comfort",
            "flx_accessibility",
            "flx_balance",
        ],
        "eff": [
            "eff_tech",
            "eff_flow",
            "eff_feedback",
            "eff_productivity",
        ],
    }

    records = []

    for group, probs in [("A", prob_A), ("B", prob_B)]:
        for _ in range(n_per_group):
            row = {"variant_group": group}

            for dim_key, cols in dimensions.items():
                for col in cols:
                    row[col] = int(rng.choice(scores, p=probs[dim_key]))

            records.append(row)

    df = pd.DataFrame(records)

    return (
        df.sample(frac=1, random_state=seed)
        .reset_index(drop=True)
    )

df_simulasi = generate_monte_carlo_survey(n_per_group=70)

print(df_simulasi.head())

```