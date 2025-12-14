import sqlite3
import os
import database
from matching import run_matching


def test_matching_results(monkeypatch):
    """
    Matching test using pre-populated labsatyale_test.sqlite (added rank.sql)
    see rank.sql for the specific test cases
    Test Case 1:
        fellowship 100 → stu102

    Test Case 2:
        fellowship 200 → stu202
    """

    test_db_path = os.path.abspath("labsatyale_test.sqlite")

    def fake_connect(_):
        return sqlite3.connect(test_db_path)

    monkeypatch.setattr(database, "connect", fake_connect)

    matches = run_matching()

    # --- ASSERTIONS (MATCH REAL RETURN TYPE) ---
    assert 100 in matches
    assert "stu102" in matches[100]

    assert 200 in matches
    assert "stu202" in matches[200]
