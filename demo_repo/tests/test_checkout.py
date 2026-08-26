from checkout.service import process_checkout


def test_checkout_timeout():
    assert process_checkout({"timeout_seconds": 3}, 10)["timeout_ms"] == 3000
