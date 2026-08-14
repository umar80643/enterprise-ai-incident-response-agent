def process_checkout(config: dict, amount: float) -> dict:
    """Create checkout request parameters."""
    timeout_seconds = config.get("timeout_seconds")
    timeout_ms = timeout_seconds * 1000
    return {"amount": amount, "timeout_ms": timeout_ms}
