"""Tests for the Analytics service: stateless assignment + the event store."""

from analytics import assign, store


def test_variant_is_deterministic():
    first = assign.variant_for("signup_box_test", "visitor-123")
    second = assign.variant_for("signup_box_test", "visitor-123")
    assert first == second
    assert first in {"A", "B"}


def test_variant_unknown_test_is_none():
    assert assign.variant_for("does_not_exist", "visitor-123") is None


def test_variant_distribution_is_roughly_even():
    counts = {"A": 0, "B": 0}
    for i in range(400):
        counts[assign.variant_for("signup_box_test", f"visitor-{i}")] += 1
    assert counts["A"] > 120 and counts["B"] > 120


def test_all_variants_covers_every_test():
    result = assign.all_variants("visitor-123")
    assert set(result) == set(assign.load_tests())


def test_store_roundtrip_and_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_FILE", str(tmp_path / "ev.sqlite"))
    monkeypatch.setattr(store, "_initialized", False)

    store.write_ab_log({"event": "variation_presented", "test": "t", "variant": "A", "visitor": "v1"})
    store.write_ab_log({"event": "variation_presented", "test": "t", "variant": "B", "visitor": "v2"})
    store.write_ab_log({"event": "signup_click", "test": "t", "variant": "A", "visitor": "v1"})

    summary = {row["variant"]: row for row in store.summarize("t")}
    assert summary["A"]["impressions"] == 1
    assert summary["A"]["actions"] == {"signup_click": 1}
    assert summary["A"]["conversion_rate"] == 1.0
    assert summary["B"]["conversion_rate"] == 0.0
