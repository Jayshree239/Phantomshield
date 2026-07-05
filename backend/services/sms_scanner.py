# d:/SPECTER/phantomshield/backend/services/sms_scanner.py
# SMS scan helpers.

import re

_URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")


def extract_urls_from_sms(message: str) -> list[str]:
    return _URL_REGEX.findall(message or "")


def score_sms_text(message: str) -> int:
    urgency_words = ["otp", "click", "win", "prize", "lottery", "free", "claim", "expire"]
    lower = (message or "").lower()
    score = sum(15 for word in urgency_words if word in lower)
    return min(score, 90)
