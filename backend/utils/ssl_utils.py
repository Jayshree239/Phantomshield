# d:/SPECTER/phantomshield/backend/utils/ssl_utils.py
import socket
import ssl
from datetime import datetime


def check_ssl_certificate(host: str, timeout: int = 5) -> dict:
    try:
        pure_host = (host or "").split(":")[0]
        context = ssl.create_default_context()
        with socket.create_connection((pure_host, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=pure_host) as secure_sock:
                cert = secure_sock.getpeercert()
                not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
                not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                return {
                    "valid": True,
                    "issued_at": not_before.isoformat(),
                    "expires_at": not_after.isoformat(),
                }
    except Exception:
        return {"valid": False, "issued_at": None, "expires_at": None}
