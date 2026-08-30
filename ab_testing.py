"""
ab_testing.py

A/B testing infrastructure for the Labs at Yale application.

This module centralizes everything needed to run an A/B test:
    - loading the test registry from ab_tests.json;
    - a before_request middleware that assigns every visitor a variant for each
      running test and keeps that assignment stable across their visits;
    - ab_test_log(), which records that a variant of a test was presented; and
    - event_logger(), which records that the target action of a test was
      performed.

Adding a new A/B test only requires adding an entry to ab_tests.json. The
middleware iterates the whole registry, so no code changes are needed here.

Expected ab_tests.json shape:

    {
        "<test_name>": {
            "variants": {
                "<variant_name>": { ...arbitrary config... },
                ...
            }
        },
        ...
    }
"""

import json
import os
import random
from datetime import datetime

from flask import request, session

from ab_test_log import write_ab_log

_TESTS_FILE = os.path.join(os.path.dirname(__file__), "ab_tests.json")


def load_tests():
    """Load and return the A/B test registry from ab_tests.json."""
    with open(_TESTS_FILE, "r") as f:
        return json.load(f)


# Loaded once at import time. Restart the server to pick up ab_tests.json edits.
AB_TESTS = load_tests()


def _session_key(test_name):
    """Session key under which this test's assigned variant is stored."""
    return f"ab_test:{test_name}"


def _assign_variant(test_name, config):
    """
    Ensure the current session has a variant assigned for test_name.

    The choice is stored in the Flask session so the same visitor always sees
    the same variant on every subsequent request. Tests with no variants are
    skipped.
    """
    key = _session_key(test_name)
    if key in session:
        return

    variants = list(config.get("variants", {}).keys())
    if not variants:
        return

    session[key] = random.choice(variants)


def ab_test_middleware():
    """
    before_request hook: assign a variant for every running A/B test.

    Registered on the app via init_app(). Skips static-asset requests so those
    responses do not needlessly set a session cookie.
    """
    if request.endpoint == "static":
        return

    for test_name, config in AB_TESTS.items():
        _assign_variant(test_name, config)


def get_variant(test_name):
    """Return the variant assigned to the current session for test_name, or None."""
    return session.get(_session_key(test_name))


def ab_test_log(test_name, variant=None):
    """
    Record that a variant of test_name was presented to the current visitor.

    If variant is not given, the visitor's assigned variant is used.
    """
    if variant is None:
        variant = get_variant(test_name)

    write_ab_log({
        "event": "variation_presented",
        "test": test_name,
        "variant": variant,
        "timestamp": datetime.now().isoformat(),
    })


def event_logger(event_name, test_name):
    """
    Record that the target action (event_name) for test_name was performed by
    the current visitor, tagged with the variant they were shown.
    """
    write_ab_log({
        "event": event_name,
        "test": test_name,
        "variant": get_variant(test_name),
        "timestamp": datetime.now().isoformat(),
    })


def init_app(app):
    """Register the A/B testing middleware on the given Flask app."""
    app.before_request(ab_test_middleware)
