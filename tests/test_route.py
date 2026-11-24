"""Functional tests. Attack tests are in test_attacks.py."""
from classifier.route import route


def test_inbox_tickets_go_to_the_right_queues():
    out = {r["id"]: r["queue"] for r in route()}
    assert out == {"101": "access", "102": "hardware", "103": "network", "104": "software"}


def test_sentiment_is_off_by_default():
    assert all(r["sentiment"] == "n/a" for r in route())
