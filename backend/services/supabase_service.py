# d:/SPECTER/phantomshield/backend/services/supabase_service.py
# Neon PostgreSQL access helpers.
# NOTE: File name is kept for backward compatibility with existing imports.

import asyncio
import logging
from collections import Counter
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row

from config import settings

logger = logging.getLogger(__name__)


def _database_url() -> str:
    return settings.NEON_DATABASE_URL or settings.DATABASE_URL


def _enum_value(value: Any) -> str:
    raw = getattr(value, "value", value)
    text = str(raw).lower().strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text


def _normalize_scan_type(value: Any) -> str:
    text = _enum_value(value)
    return text if text in {"url", "email", "sms"} else "url"


def _connect() -> Optional[psycopg.Connection]:
    database_url = _database_url()
    if not database_url:
        return None

    try:
        return psycopg.connect(
            database_url,
            row_factory=dict_row,
            autocommit=True,
            connect_timeout=settings.DB_CONNECT_TIMEOUT,
        )
    except Exception as exc:
        logger.warning("Neon connection failed: %s", exc)
        return None


def _upsert_user_profile_sync(conn: psycopg.Connection, user_id: str, payload: Dict[str, Any]) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT total_scans, phishing_caught, weak_spots
            FROM user_profiles
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,),
        )
        row = cursor.fetchone()

        if row:
            total_scans = int(row.get("total_scans", 0)) + 1
            phishing_caught = int(row.get("phishing_caught", 0)) + int(bool(payload["is_phishing"]))
            weak_spots = list(row.get("weak_spots") or [])
            weak_spots.extend(payload.get("attack_types") or [])

            weak_spot_counts = Counter(weak_spots)
            top_weak_spots = [name for name, _count in weak_spot_counts.most_common(5)]
            security_score = max(0, min(100, 100 - (phishing_caught * 3) + (total_scans // 5)))

            cursor.execute(
                """
                UPDATE user_profiles
                SET total_scans = %s,
                    phishing_caught = %s,
                    weak_spots = %s,
                    security_score = %s,
                    last_active = NOW()
                WHERE user_id = %s
                """,
                (total_scans, phishing_caught, top_weak_spots, security_score, user_id),
            )
            return

        cursor.execute(
            """
            INSERT INTO user_profiles (user_id, total_scans, phishing_caught, security_score, weak_spots)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                1,
                int(bool(payload["is_phishing"])),
                50,
                payload.get("attack_types") or [],
            ),
        )


async def save_scan_result(user_id: str, scan_data: Dict[str, Any], attack_types: List[str]) -> None:
    explanation = scan_data.get("explanation") or {}
    payload = {
        "user_id": user_id,
        "scan_type": _normalize_scan_type(scan_data.get("scan_type", "url")),
        "input_value": scan_data.get("input_value", ""),
        "threat_score": int(scan_data.get("threat_score", 0)),
        "threat_level": _enum_value(scan_data.get("threat_level", "safe")),
        "is_phishing": bool(scan_data.get("is_phishing", False)),
        "confidence": float(scan_data.get("confidence", 0.0)),
        "attack_types": attack_types,
        "ai_explanation": explanation.get("ai_explanation") if isinstance(explanation, dict) else None,
        "scan_time_ms": int(scan_data.get("scan_time_ms", 0)),
    }

    def _save_sync() -> None:
        conn = _connect()
        if conn is None:
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scan_results (
                        user_id,
                        scan_type,
                        input_value,
                        threat_score,
                        threat_level,
                        is_phishing,
                        confidence,
                        attack_types,
                        ai_explanation,
                        scan_time_ms
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        payload["user_id"],
                        payload["scan_type"],
                        payload["input_value"],
                        payload["threat_score"],
                        payload["threat_level"],
                        payload["is_phishing"],
                        payload["confidence"],
                        payload["attack_types"],
                        payload["ai_explanation"],
                        payload["scan_time_ms"],
                    ),
                )

            _upsert_user_profile_sync(conn, user_id, payload)
        except Exception as exc:
            logger.warning("Failed to persist scan result: %s", exc)
        finally:
            conn.close()

    await asyncio.to_thread(_save_sync)


async def get_user_weak_spots(user_id: str) -> List[str]:
    def _read_sync() -> List[str]:
        conn = _connect()
        if conn is None:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT weak_spots FROM user_profiles WHERE user_id = %s LIMIT 1",
                    (user_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return []
                return list(row.get("weak_spots") or [])
        except Exception:
            return []
        finally:
            conn.close()

    return await asyncio.to_thread(_read_sync)


async def get_user_scan_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    safe_limit = max(1, min(limit, 500))

    def _read_sync() -> List[Dict[str, Any]]:
        conn = _connect()
        if conn is None:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id::text AS id,
                        user_id,
                        scan_type,
                        input_value,
                        threat_score,
                        threat_level,
                        is_phishing,
                        confidence,
                        attack_types,
                        ai_explanation,
                        scan_time_ms,
                        created_at,
                        created_at AS timestamp
                    FROM scan_results
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, safe_limit),
                )
                return [dict(row) for row in (cursor.fetchall() or [])]
        except Exception:
            return []
        finally:
            conn.close()

    return await asyncio.to_thread(_read_sync)


async def get_user_dashboard_stats(user_id: str) -> Dict[str, Any]:
    default_stats = {
        "total_scans": 0,
        "phishing_caught": 0,
        "safe_count": 0,
        "top_attack_type": None,
        "security_score": 50,
    }

    def _read_sync() -> Dict[str, Any]:
        conn = _connect()
        if conn is None:
            return default_stats

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*)::INT AS total_scans,
                        COUNT(*) FILTER (WHERE is_phishing)::INT AS phishing_caught,
                        COUNT(*) FILTER (WHERE NOT is_phishing)::INT AS safe_count
                    FROM scan_results
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                counts = cursor.fetchone() or {}

                cursor.execute(
                    """
                    SELECT attack_type
                    FROM (
                        SELECT unnest(attack_types) AS attack_type
                        FROM scan_results
                        WHERE user_id = %s AND is_phishing
                    ) attacks
                    GROUP BY attack_type
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                    """,
                    (user_id,),
                )
                attack_row = cursor.fetchone()

                total_scans = int(counts.get("total_scans", 0))
                phishing_caught = int(counts.get("phishing_caught", 0))
                safe_count = int(counts.get("safe_count", 0))

                return {
                    "total_scans": total_scans,
                    "phishing_caught": phishing_caught,
                    "safe_count": safe_count,
                    "top_attack_type": attack_row.get("attack_type") if attack_row else None,
                    "security_score": max(0, min(100, safe_count * 5)),
                }
        except Exception as exc:
            logger.warning("Failed to read dashboard stats: %s", exc)
            return default_stats
        finally:
            conn.close()

    return await asyncio.to_thread(_read_sync)

