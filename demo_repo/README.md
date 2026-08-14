# Checkout demo
A deployment changed `checkout.timeout_seconds` to null. Checkout code assumes a numeric value, producing a TypeError and HTTP 500 upstream.
