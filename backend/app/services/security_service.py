import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above",
    r"disregard\s+(all\s+)?previous",
    r"you\s+are\s+now",
    r"new\s+instructions?\s*:",
    r"system\s+prompt",
    r"<\s*script",
    r"javascript\s*:",
    r"override\s+(your|the)\s+(instructions|rules|guidelines)",
    r"bypass\s+(your|the|all)\s+(safety|security|filters|restrictions)",
    r"pretend\s+you\s+are",
    r"act\s+as\s+(if|a)\s+",
    r"jailbreak",
    r"DAN\s+mode",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

MAX_INPUT_LENGTH = 4000


def detect_injection(text: str) -> bool:
    for pattern in _compiled_patterns:
        if pattern.search(text):
            return True
    return False


def sanitize_input(text: str) -> str:
    # Limit length
    text = text[:MAX_INPUT_LENGTH]
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove null bytes
    text = text.replace("\x00", "")
    return text
