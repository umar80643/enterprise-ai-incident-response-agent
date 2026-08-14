SUSPICIOUS = ("ignore previous", "system prompt", "developer message", "exfiltrate", "reveal secret")

def wrap_untrusted_evidence(text: str) -> str:
    return "<UNTRUSTED_REPOSITORY_EVIDENCE>\n" + text + "\n</UNTRUSTED_REPOSITORY_EVIDENCE>"

def contains_prompt_injection(text: str) -> bool:
    low = text.lower()
    return any(x in low for x in SUSPICIOUS)
