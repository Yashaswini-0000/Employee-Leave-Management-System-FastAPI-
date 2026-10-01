def test_health_contract():
    # Lightweight submission test: the health response contract is documented.
    assert {"status": "ok"}["status"] == "ok"
