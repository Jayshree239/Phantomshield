# d:/SPECTER/phantomshield/backend/services/education_service.py
# Personalized security education and tips.

from typing import List, Optional


_TIPS_DATABASE = {
    "homograph": {
        "title": "The Look-Alike Letter Trick",
        "content": (
            "Attackers replace letters with similar-looking characters. "
            "Always inspect URLs character by character before trusting them."
        ),
        "example": "paypal.com -> paypa0.com (zero instead of letter o)",
        "category": "homograph",
        "difficulty": "intermediate",
    },
    "urgency_manipulation": {
        "title": "The Panic Button Attack",
        "content": (
            "Phishing content uses words like URGENT and SUSPENDED to force rushed clicks. "
            "Pause and verify through official channels."
        ),
        "example": "Your account will be suspended in 24 hours. Click here.",
        "category": "urgency",
        "difficulty": "beginner",
    },
    "brand_impersonation": {
        "title": "The Evil Twin Domain",
        "content": (
            "A fake domain can include a trusted brand name and still be malicious. "
            "Verify the exact root domain every time."
        ),
        "example": "amazon.com (real) vs amazon-secure-login.com (fake)",
        "category": "brand_impersonation",
        "difficulty": "beginner",
    },
    "fake_ssl": {
        "title": "The HTTPS Lie",
        "content": (
            "HTTPS means encryption, not legitimacy. "
            "Phishing websites can also have SSL certificates."
        ),
        "example": "https://paypa0.com can still be phishing",
        "category": "ssl",
        "difficulty": "intermediate",
    },
    "typosquatting": {
        "title": "The One-Letter Trap",
        "content": (
            "Typosquatting domains exploit common typing mistakes. "
            "Use bookmarks for important services."
        ),
        "example": "gogle.com, facebok.com, microsooft.com",
        "category": "typosquatting",
        "difficulty": "beginner",
    },
    "default": {
        "title": "The Golden Rule of Links",
        "content": (
            "Do not click links in unsolicited messages. "
            "Visit websites directly by typing known addresses or using bookmarks."
        ),
        "example": "Received a bank warning? Open your bank site manually.",
        "category": "general",
        "difficulty": "beginner",
    },
}


def generate_education_tip(
    attack_types: List[str],
    user_weak_spots: Optional[List[str]] = None,
) -> dict:
    tip_key = "default"

    for attack in attack_types:
        if attack in _TIPS_DATABASE:
            tip_key = attack
            break

    if user_weak_spots:
        for weak_spot in user_weak_spots:
            if weak_spot in _TIPS_DATABASE:
                tip_key = weak_spot
                break

    tip = _TIPS_DATABASE[tip_key]
    return {
        "tip_id": f"tip_{tip_key}_{hash(str(attack_types)) % 10000}",
        **tip,
    }


def get_education_library() -> list[dict]:
    return [
        {
            "tip_id": f"library_{key}",
            **value,
        }
        for key, value in _TIPS_DATABASE.items()
        if key != "default"
    ]
