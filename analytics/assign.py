"""
Stateless A/B variant assignment.

The variant a visitor sees is derived by hashing (visitor_id, test_name), so:
    - the same visitor always gets the same variant for a test, with no stored
      state and no session;
    - the split across variants is uniform;
    - a new test added to ab_tests.json takes effect immediately.

The test registry lives in ab_tests.json, owned by this service.
"""

import hashlib
import json
import os

_TESTS_FILE = os.path.join(os.path.dirname(__file__), "ab_tests.json")


def load_tests():
    """Return the A/B test registry from ab_tests.json."""
    with open(_TESTS_FILE, "r") as f:
        return json.load(f)


def variant_for(test_name, visitor_id, tests=None):
    """
    Return the variant `visitor_id` should see for `test_name`.

    Returns None if the test is unknown or has no variants. If `visitor_id` is
    missing, the first variant is used as a stable default. Pass `tests` to
    reuse an already-loaded registry.
    """
    tests = load_tests() if tests is None else tests
    config = tests.get(test_name) or {}
    variants = list(config.get("variants", {}).keys())
    if not variants:
        return None
    if not visitor_id:
        return variants[0]
    digest = hashlib.sha256(f"{visitor_id}:{test_name}".encode()).hexdigest()
    return variants[int(digest, 16) % len(variants)]


def all_variants(visitor_id):
    """Return {test_name: variant} for every running test."""
    tests = load_tests()
    return {name: variant_for(name, visitor_id, tests) for name in tests}
