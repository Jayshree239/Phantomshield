# d:/SPECTER/phantomshield/backend/utils/domain_utils.py
import logging
import socket
from contextlib import contextmanager
from datetime import datetime

import concurrent

import whois


logger = logging.getLogger(__name__)


def _get_whois_timeout() -> int:
    try:
        from config import settings

        return max(1, int(getattr(settings, "WHOIS_TIMEOUT", 3)))
    except Exception:
        return 10


@contextmanager
def _temporary_socket_timeout(timeout_seconds: int):
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout_seconds)
    try:
        yield
    finally:
        socket.setdefaulttimeout(previous_timeout)


@contextmanager
def _suppress_whois_noise():
    targets = [logging.getLogger("whois"), logging.getLogger("whois.whois")]
    previous = [(logger.level, logger.propagate) for logger in targets]

    for target in targets:
        target.setLevel(logging.CRITICAL)
        target.propagate = False

    try:
        yield
    finally:
        for target, (level, propagate) in zip(targets, previous):
            target.setLevel(level)
            target.propagate = propagate


def is_ip_address(host: str) -> bool:
    try:
        socket.inet_aton((host or "").split(":")[0])
        return True
    except OSError:
        return False


def get_domain_age_days(domain: str) -> int | None:
    domain = (domain or "").strip()
    if not domain:
        return None

    try:
        import whois

        with _temporary_socket_timeout(_get_whois_timeout()), _suppress_whois_noise():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(whois.whois, domain)
                record = future.result(timeout=3)

        created = record.creation_date
        if isinstance(created, list):
            created = created[0]
        if created:
            now = datetime.now(created.tzinfo) if getattr(created, "tzinfo", None) else datetime.now()
            return max(0, (now - created).days)
    except Exception as exc:
        logger.debug("WHOIS lookup failed for %s: %s", domain, exc)
        return None

    return None
