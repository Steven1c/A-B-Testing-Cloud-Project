"""Uji Mann-Whitney."""
from dataclasses import dataclass, asdict
from typing import Mapping, Sequence

import numpy as np
from scipy.stats import mannwhitneyu

from src.contract import MIN_N, PRIMARY_ITEM
from src.errors import InvalidScoreError, InsufficientSampleError  # noqa: F401 (diekspor ulang)


@dataclass
class TestResult:
    test_name: str
    outcome_column: str
    n_a: int
    n_b: int
    median_a: float
    median_b: float
    statistic: float
    p_value: float
    effect_size: float
    ci_lower: float
    ci_upper: float
    alpha: float
    decision: str
    interpretation: str

    def to_dict(self) -> dict:
        return asdict(self)


def _validate(scores: Sequence[int]) -> np.ndarray:
    arr = np.asarray(scores)
    if arr.size and (not np.issubdtype(arr.dtype, np.integer) or arr.min() < 1 or arr.max() > 5):
        raise InvalidScoreError("Skor harus integer 1-5.")
    return arr


def run_mann_whitney(scores_a: Sequence[int], scores_b: Sequence[int], alpha: float = 0.05,
                     outcome_column: str = PRIMARY_ITEM, n_boot: int = 2000, seed: int = 42) -> TestResult:
    """Uji Mann-Whitney U dua arah, Luring (A) vs Daring (B), pada satu butir (default Q1 sat_overall)."""
    a, b = _validate(scores_a), _validate(scores_b)
    if len(a) < MIN_N or len(b) < MIN_N:
        raise InsufficientSampleError(
            f"Data belum cukup (min. {MIN_N} per metode). Saat ini: Luring n={len(a)}, Daring n={len(b)}.")

    u, p = mannwhitneyu(a, b, alternative="two-sided", method="asymptotic", use_continuity=True)
    effect = 2 * u / (len(a) * len(b)) - 1  # rank-biserial (A relatif terhadap B)

    # Selang kepercayaan bootstrap untuk estimasi Hodges-Lehmann (selisih lokasi A - B)
    rng = np.random.default_rng(seed)
    hl = lambda x, y: float(np.median(np.subtract.outer(x, y)))
    boots = [hl(rng.choice(a, len(a)), rng.choice(b, len(b))) for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    reject = p < alpha
    decision = "tolak H0" if reject else "gagal menolak H0"
    interp = (f"Pada alpha {alpha}, {decision}: "
              + ("terdapat bukti perbedaan distribusi skor kepuasan antara Luring dan Daring."
                 if reject else "tidak cukup bukti adanya perbedaan skor kepuasan antara Luring dan Daring."))
    return TestResult("mann_whitney_u", outcome_column, len(a), len(b),
                      float(np.median(a)), float(np.median(b)), float(u), float(p), float(effect),
                      float(lo), float(hi), alpha, decision, interp)


def describe_items(item_scores: Mapping[str, Mapping[str, Sequence[int]]]) -> list[dict]:
    """Ringkasan deskriptif per butir (tanpa uji inferensial).
    Input: {butir: {"A": [...], "B": [...]}}. Output: daftar {item, n_a, n_b, median_a, median_b}."""
    rows = []
    for item, per in item_scores.items():
        a, b = list(per.get("A", [])), list(per.get("B", []))
        rows.append({
            "item": item, "n_a": len(a), "n_b": len(b),
            "median_a": float(np.median(a)) if a else None,
            "median_b": float(np.median(b)) if b else None,
        })
    return rows
