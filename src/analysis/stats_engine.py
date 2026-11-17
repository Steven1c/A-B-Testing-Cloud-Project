"""uUi Mann-Whitney"""
from dataclasses import dataclass, asdict
from typing import Sequence
import numpy as np
from scipy.stats import mannwhitneyu

from src.errors import InvalidScoreError, InsufficientSampleError  # noqa: F401 (diekspor ulang)

MIN_N = 10  # minimum per varian agar uji dihitung (lihat kontrak Bagian 6)


@dataclass
class TestResult:
    test_name: str
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


def run_mann_whitney(scores_a: Sequence[int], scores_b: Sequence[int],
                     alpha: float = 0.05, n_boot: int = 2000, seed: int = 42) -> TestResult:
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
    return TestResult("mann_whitney_u", len(a), len(b), float(np.median(a)), float(np.median(b)),
                      float(u), float(p), float(effect), float(lo), float(hi), alpha, decision, interp)
