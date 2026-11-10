"""
stats_engine.py
Modul inti komputasi analisis statistik inferensial untuk pengujian A/B.
Disediakan oleh Analysis Layer untuk diintegrasikan ke antarmuka web Streamlit.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestIndPower
from statsmodels.stats.proportion import proportions_ztest


def compute_sample_size(effect_size: float = 0.35, alpha: float = 0.05, power: float = 0.80) -> int:
    """
    Menghitung ukuran sampel minimum N per varian berdasarkan Power Analysis.
    Default: Cohen's d = 0.35 (medium-low), alpha = 0.05, power = 0.80.
    """
    analysis = TTestIndPower()
    sample_size = analysis.solve_power(effect_size=effect_size, power=power, alpha=alpha, ratio=1.0)
    return int(np.ceil(sample_size))


def analyze_ab_test(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """
    Menjalankan pengujian hipotesis lengkap pada dataset respons A/B:
    1. Uji Normalitas (Shapiro-Wilk)
    2. Uji Homogenitas Varians (Levene)
    3. Uji Hipotesis Rata-rata Kontinu (Welch's t-test)
    4. 95% Confidence Interval selisih mean (B - A)
    5. Uji Proporsi Konversi (Two-proportion Z-test)
    6. Keputusan formal: 'Tolak H₀' atau 'Gagal menolak H₀'
    """
    if df.empty or "assigned_variant" not in df.columns:
        return {"status": "error", "message": "Dataset kosong atau format kolom tidak sesuai."}

    group_a = df[df["assigned_variant"] == "A"]
    group_b = df[df["assigned_variant"] == "B"]

    n_a = len(group_a)
    n_b = len(group_b)

    if n_a < 3 or n_b < 3:
        return {
            "status": "warning",
            "message": f"Sampel belum memadai untuk uji inferensial (N_A={n_a}, N_B={n_b}). Minimal 3 per varian."
        }

    # --- 1. Statistik Deskriptif ---
    scores_a = group_a["willingness_to_pay"].dropna().values
    scores_b = group_b["willingness_to_pay"].dropna().values

    mean_a = float(np.mean(scores_a))
    mean_b = float(np.mean(scores_b))
    std_a = float(np.std(scores_a, ddof=1)) if n_a > 1 else 0.0
    std_b = float(np.std(scores_b, ddof=1)) if n_b > 1 else 0.0

    # --- 2. Uji Asumsi ---
    # Normalitas Shapiro-Wilk (maks 5000 sampel)
    shapiro_a_p = float(stats.shapiro(scores_a)[1]) if n_a >= 3 else 1.0
    shapiro_b_p = float(stats.shapiro(scores_b)[1]) if n_b >= 3 else 1.0
    is_normal = (shapiro_a_p > 0.05) and (shapiro_b_p > 0.05)

    # Homogenitas Varians (Levene's test)
    levene_stat, levene_p = stats.levene(scores_a, scores_b)
    is_equal_var = float(levene_p) > 0.05

    # --- 3. Uji Hipotesis Utama (Two-sample Welch's t-test) ---
    # H0: mu_B <= mu_A vs H1: mu_B > mu_A (One-tailed)
    t_stat, t_p_two_tailed = stats.ttest_ind(scores_b, scores_a, equal_var=is_equal_var)
    
    # Konversi ke p-value one-tailed (arah B > A)
    if t_stat > 0:
        p_value_continuous = float(t_p_two_tailed / 2.0)
    else:
        p_value_continuous = float(1.0 - (t_p_two_tailed / 2.0))

    # --- 4. 95% Confidence Interval untuk Selisih Mean (mu_B - mu_A) ---
    diff_mean = mean_b - mean_a
    se_diff = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
    
    # Welch–Satterthwaite degrees of freedom
    if se_diff > 0:
        df_welch = ((std_a**2 / n_a + std_b**2 / n_b)**2) / (
            ((std_a**2 / n_a)**2 / (n_a - 1)) + ((std_b**2 / n_b)**2 / (n_b - 1))
        )
        t_crit = stats.t.ppf(1.0 - (alpha / 2.0), df=df_welch)
        ci_lower = float(diff_mean - (t_crit * se_diff))
        ci_upper = float(diff_mean + (t_crit * se_diff))
    else:
        ci_lower, ci_upper = diff_mean, diff_mean

    # Keputusan Uji Kontinu
    if p_value_continuous < alpha:
        decision_continuous = "Tolak H₀"
        conclusion_desc = (
            f"Tolak H₀ pada tingkat signifikansi {int(alpha*100)}% (p-value = {p_value_continuous:.4f} < {alpha}). "
            f"Terdapat bukti statistik yang cukup bahwa Varian B menghasilkan skor kesediaan membayar lebih tinggi secara signifikan."
        )
    else:
        decision_continuous = "Gagal menolak H₀"
        conclusion_desc = (
            f"Gagal menolak H₀ pada tingkat signifikansi {int(alpha*100)}% (p-value = {p_value_continuous:.4f} >= {alpha}). "
            f"Belum cukup bukti statistik untuk menyatakan Varian B lebih unggul dari Varian A."
        )

    # --- 5. Uji Proporsi Konversi Klik (Two-Proportion Z-Test) ---
    clicks_a = int(group_a["clicked_signup"].sum())
    clicks_b = int(group_b["clicked_signup"].sum())
    cr_a = float(clicks_a / n_a) if n_a > 0 else 0.0
    cr_b = float(clicks_b / n_b) if n_b > 0 else 0.0

    try:
        count = np.array([clicks_b, clicks_a])
        nobs = np.array([n_b, n_a])
        z_stat, z_p_val = proportions_ztest(count, nobs, alternative='larger')
        z_p_val = float(z_p_val)
    except Exception:
        z_stat, z_p_val = 0.0, 1.0

    return {
        "status": "success",
        "sample_size": {"total": n_a + n_b, "n_a": n_a, "n_b": n_b},
        "descriptive": {
            "mean_a": round(mean_a, 2),
            "std_a": round(std_a, 2),
            "mean_b": round(mean_b, 2),
            "std_b": round(std_b, 2),
            "diff_mean": round(diff_mean, 2)
        },
        "assumptions": {
            "shapiro_a_p": round(shapiro_a_p, 4),
            "shapiro_b_p": round(shapiro_b_p, 4),
            "is_normal": is_normal,
            "levene_p": round(float(levene_p), 4),
            "is_equal_var": is_equal_var
        },
        "continuous_test": {
            "test_name": "Welch's Two-Sample t-test (One-tailed)",
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(p_value_continuous, 4),
            "ci_95": [round(ci_lower, 2), round(ci_upper, 2)],
            "decision": decision_continuous,
            "conclusion": conclusion_desc
        },
        "proportion_test": {
            "cr_a": round(cr_a * 100, 1),
            "cr_b": round(cr_b * 100, 1),
            "z_statistic": round(float(z_stat), 4),
            "p_value": round(z_p_val, 4),
            "decision": "Tolak H₀" if z_p_val < alpha else "Gagal menolak H₀"
        }
    }
