"""Uji kepatuhan kode terhadap Interface Contract (docs/interface-contract.md).

Jalankan dari root repo:  pytest tests/ -v
Bagian database bersifat opt-in (lihat bawah) karena menulis ke database sungguhan.
"""
import os
import pytest

# Sesuaikan jalur impor ini bila nama modul/kelas di kode tim berbeda
from src.analysis.stats_engine import (
    run_mann_whitney, InvalidScoreError, InsufficientSampleError,
)
from src.analysis.simulate_data import generate_responses

# Field output Bagian 2 kontrak
OUTPUT_FIELDS = [
    "test_name", "n_a", "n_b", "median_a", "median_b", "statistic", "p_value",
    "effect_size", "ci_lower", "ci_upper", "alpha", "decision", "interpretation",
]
MIN_N = 10  # samakan dengan kontrak Bagian 6


@pytest.fixture(scope="module")
def sim():
    return generate_responses(40, 40, seed=1)


@pytest.fixture(scope="module")
def result(sim):
    a = sim.loc[sim.variant == "A", "score"].tolist()
    b = sim.loc[sim.variant == "B", "score"].tolist()
    return run_mann_whitney(a, b)


# ---- Input / data simulasi (kontrak Bagian 1) ----
def test_simulated_columns(sim):
    assert {"session_id", "variant", "score"} <= set(sim.columns)


def test_simulated_variant_values(sim):
    assert set(sim["variant"].unique()) <= {"A", "B"}


def test_simulated_score_range(sim):
    assert sim["score"].between(1, 5).all()
    assert str(sim["score"].dtype).startswith("int")


def test_simulated_session_unique(sim):
    assert sim["session_id"].is_unique


# ---- Output analisis (kontrak Bagian 2) ----
@pytest.mark.parametrize("field", OUTPUT_FIELDS)
def test_output_has_field(result, field):
    assert hasattr(result, field)


def test_test_name(result):
    assert result.test_name == "mann_whitney_u"


def test_p_value_range(result):
    assert 0.0 <= result.p_value <= 1.0


def test_ci_order(result):
    assert result.ci_lower <= result.ci_upper


def test_decision_rule(result):
    expected = "tolak H0" if result.p_value < result.alpha else "gagal menolak H0"
    assert result.decision == expected


# ---- Perilaku saat gagal (kontrak Bagian 6) ----
def test_small_sample_raises():
    with pytest.raises(InsufficientSampleError):
        run_mann_whitney([3] * (MIN_N - 1), [4] * MIN_N)


@pytest.mark.parametrize("bad", [0, 6, -1])
def test_out_of_range_score_raises(bad):
    with pytest.raises(InvalidScoreError):
        run_mann_whitney([3] * MIN_N + [bad], [4] * MIN_N)


def test_float_score_raises():
    with pytest.raises(InvalidScoreError):
        run_mann_whitney([3.5] * MIN_N, [4] * MIN_N)


# ---- Database (OPT-IN) ----
# Menulis ke database sungguhan. Jalankan hanya pada proyek/tabel uji:
#   RUN_DB_TESTS=1 pytest tests/ -v
# Sesuaikan nama modul/fungsi/exception dengan db.py tim Infrastructure.
db_only = pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="set RUN_DB_TESTS=1 untuk uji database")


@db_only
def test_db_insert_valid_and_duplicate():
    from src.app import db
    sid = f"test_{os.urandom(4).hex()}"
    assert isinstance(db.insert_response(sid, "A", 4), str)
    with pytest.raises(db.DuplicateSessionError):
        db.insert_response(sid, "A", 4)


@db_only
@pytest.mark.parametrize("variant,score", [("C", 3), ("A", 0), ("A", 6)])
def test_db_rejects_invalid(variant, score):
    from src.app import db
    with pytest.raises(Exception):
        db.insert_response(f"test_{os.urandom(4).hex()}", variant, score)


@db_only
def test_db_fetch_scores_shape():
    from src.app import db
    data = db.fetch_scores()
    assert set(data) == {"A", "B"}
