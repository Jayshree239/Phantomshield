# d:/SPECTER/phantomshield/backend/routers/dashboard.py
# User dashboard endpoints.

from collections import Counter

from fastapi import APIRouter

from services.supabase_service import get_user_dashboard_stats, get_user_scan_history

router = APIRouter()


@router.get("/{user_id}")
async def get_dashboard(user_id: str):
    stats = await get_user_dashboard_stats(user_id)
    history = await get_user_scan_history(user_id, limit=50)

    weak_spot_counter = Counter(
        attack
        for scan in history
        for attack in (scan.get("attack_types") or [])
        if attack
    )

    weak_spots = [
        {"attack_type": attack_type, "count": count}
        for attack_type, count in weak_spot_counter.most_common(5)
    ]

    trend_data = []
    for index, scan in enumerate(reversed(history[-7:])):
        trend_data.append(
            {
                "day": index + 1,
                "phishing": 1 if scan.get("is_phishing") else 0,
                "safe": 0 if scan.get("is_phishing") else 1,
            }
        )

    return {
        "user_id": user_id,
        "stats": stats,
        "scan_history": history,
        "weak_spots": weak_spots,
        "trend": trend_data,
        "improvement_trend": "improving" if stats.get("safe_count", 0) >= stats.get("phishing_caught", 0) else "declining",
    }

