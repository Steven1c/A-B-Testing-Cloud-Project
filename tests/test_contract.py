"""Uji kepatuhan kode terhadap Interface Contract v1.1 (docs/interface-contract.md).

Jalankan dari root repo:  pytest tests/ -v
Uji database sungguhan bersifat opt-in (RUN_DB_TESTS=1) karena menulis ke database.
"""
import os
import re
from pathlib import Path

import pytest

from src.analysis.simulate_data import generate_responses
from src.analysis.stats_engine import (
    InsufficientSampleError, InvalidScoreError, describe_items, run_mann_whitney,
)
from src.app.questions import DIMENSIONS
from src.contract import ITEM_COLUMNS, MIN_N, PRIMARY_ITEM

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FIELDS = [
    "test_name", "outcome_column", "n_a", "n_b", "median_a", "median_b", "statistic", "p_value",
    "effect_size", "ci_lower", "ci_upper", "alpha", "decision", "interpretation",
]


@pytest.fixture(scope="module")
def sim():
    return generate_responses(40, 40, seed=1)


@pytest.fixture(scope="module")
def result(sim):
    a = sim.loc[sim.variant_group == "A", PRIMARY_ITEM].tolist()
    b = sim.loc[sim.variant_group == "B", PRIMARY_ITEM].tolist()
    return run_mann_whitney(a, b)


# ---- Definisi butir (kontrak Bagian 1) ----
def test_twenty_unique_items():
    assert len(ITEM_COLUMNS) == 20 and len(set(ITEM_COLUMNS)) == 20
    assert ITEM_COLUMNS[0] == PRIMARY_ITEM == "sat_overall"


def test_questions_match_contract_items():
    cols = [col for _, items in DIMENSIONS for _no, col, _a, _b in items]
    assert tuple(cols) == ITEM_COLUMNS
    for _, items in DIMENSIONS:
        for _no, _col, ta, tb in items:
            assert ta.strip() and tb.strip()


def test_schema_sql_matches_contract():
    sql = (ROOT / "src" / "infra" / "schema.sql").read_text()
    assert "survey_responses" in sql
    assert re.search(r"session_id\s+VARCHAR\(64\)\s+NOT NULL\s+UNIQUE", sql)
    assert "variant_group IN ('A', 'B')" in sql
    for c in ITEM_COLUMNS:
        assert f"{c} BETWEEN 1 AND 5" in sql, c


# ---- Data simulasi ----
def test_simulated_columns(sim):
    assert list(sim.columns) == ["session_id", "variant_group", *ITEM_COLUMNS]


def test_simulated_variant_values(sim):
    assert set(sim["variant_group"].unique()) == {"A", "B"}


def test_simulated_score_range(sim):
    for c in ITEM_COLUMNS:
        assert sim[c].between(1, 5).all() and str(sim[c].dtype).startswith("int")


def test_simulated_session_unique(sim):
    assert sim["session_id"].is_unique and sim["session_id"].str.len().max() <= 64


# ---- Output analisis ----
@pytest.mark.parametrize("field", OUTPUT_FIELDS)
def test_output_has_field(result, field):
    assert hasattr(result, field)


def test_test_name_and_outcome(result):
    assert result.test_name == "mann_whitney_u" and result.outcome_column == "sat_overall"


def test_p_value_range(result):
    assert 0.0 <= result.p_value <= 1.0


def test_ci_order(result):
    assert result.ci_lower <= result.ci_upper


def test_decision_rule(result):
    assert result.decision == ("tolak H0" if result.p_value < result.alpha else "gagal menolak H0")


def test_describe_items_shape(sim):
    data = {c: {v: sim.loc[sim.variant_group == v, c].tolist() for v in "AB"} for c in ITEM_COLUMNS}
    rows = describe_items(data)
    assert [r["item"] for r in rows] == list(ITEM_COLUMNS)
    assert all(set(r) == {"item", "n_a", "n_b", "median_a", "median_b"} for r in rows)
    assert rows[0]["n_a"] == 40 and rows[0]["n_b"] == 40


# ---- Perilaku saat gagal ----
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


# ---- Database ----
db_only = pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="set RUN_DB_TESTS=1 untuk uji database")
ANSWERS = {c: 3 for c in ITEM_COLUMNS}


@db_only
def test_db_insert_valid_and_duplicate():
    from src.app import db
    from src.errors import DuplicateSessionError
    sid = f"test_{os.urandom(4).hex()}"
    assert isinstance(db.insert_response(sid, "A", ANSWERS), str)
    with pytest.raises(DuplicateSessionError):
        db.insert_response(sid, "A", ANSWERS)


@db_only
@pytest.mark.parametrize("variant,score", [("C", 3), ("A", 0), ("A", 6)])
def test_db_rejects_invalid(variant, score):
    from src.app import db
    with pytest.raises(Exception):
        db.insert_response(f"test_{os.urandom(4).hex()}", variant, {**ANSWERS, "sat_overall": score})


@db_only
def test_db_rejects_incomplete():
    from src.app import db
    from src.errors import IncompleteResponseError
    with pytest.raises(IncompleteResponseError):
        db.insert_response(f"test_{os.urandom(4).hex()}", "A", {"sat_overall": 3})


@db_only
def test_db_fetch_shapes():
    from src.app import db
    assert set(db.fetch_scores()) == {"A", "B"}
    assert set(db.fetch_all_item_scores()) == set(ITEM_COLUMNS)
