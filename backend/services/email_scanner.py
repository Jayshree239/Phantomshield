# d:/SPECTER/phantomshield/backend/services/email_scanner.py
# Email scan helpers.

import re

_URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def extract_urls_from_email(body: str) -> list[str]:
    return _URL_REGEX.findall(body or "")


def score_email_text(body: str) -> int:
    urgency_words = ["urgent", "immediately", "expire", "suspend", "verify", "confirm"]
    lower = (body or "").lower()
    urgency_count = sum(1 for word in urgency_words if word in lower)
    return min(urgency_count * 15, 85)
