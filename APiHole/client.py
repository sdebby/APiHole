"""Client for the Pi-hole v6 REST API."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

import requests

from .exceptions import (
    AuthenticationError,
    PiHoleConnectionError,
    PiHoleError,
    error_from_response,
)

logger = logging.getLogger(__name__)

JSON = Dict[str, Any]


def _quote(value: str) -> str:
    """Escape a domain or regex so it is safe as a single URL path segment."""
    return quote(value, safe="")


class PiHole:
    """A session with one Pi-hole v6 instance.

    Use it as a context manager so the API session is always released::

        with PiHole("pi.hole", "app-password") as ph:
            print(ph.summary())

    - ``host``: hostname or IP, optionally with ``:port``.
    - ``password``: the web password or, preferably, an app password.
      ``None`` for a Pi-hole that has no password set.
    - ``https``: use ``https://`` instead of ``http://``.
    - ``verify``: TLS verification, passed to requests (``False`` or a CA bundle path).
    - ``timeout``: seconds per request.
    - ``totp``: current 2FA code, only needed when 2FA is enabled and you are
      not using an app password.
    """

    def __init__(
        self,
        host: str = "pi.hole",
        password: Optional[str] = None,
        *,
        https: bool = False,
        verify: Union[bool, str] = True,
        timeout: float = 10,
        totp: Optional[Union[int, str]] = None,
    ) -> None:
        self.host = host
        self.password = password
        self.totp = totp
        self.timeout = timeout
        self.base_url = f"{'https' if https else 'http'}://{host}/api"
        self._session = requests.Session()
        self._session.verify = verify
        self._sid: Optional[str] = None

    # -- session handling -------------------------------------------------

    def __enter__(self) -> "PiHole":
        if self.password is not None:
            self.login()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    @property
    def authenticated(self) -> bool:
        """True while this client holds an API session."""
        return self._sid is not None

    def login(self) -> None:
        """Open an API session. Called automatically when needed."""
        if self.password is None:
            return
        payload: JSON = {"password": self.password}
        if self.totp is not None:
            payload["totp"] = int(self.totp)
        self._set_sid(None)
        resp = self._send("POST", "/auth", json=payload)
        if not resp.ok:
            raise error_from_response(resp)
        session = resp.json().get("session") or {}
        if not session.get("valid") or not session.get("sid"):
            raise AuthenticationError(
                session.get("message") or "Login failed",
                status_code=resp.status_code,
                response=resp,
            )
        self._set_sid(session["sid"])
        logger.debug("Logged in to %s", self.host)

    def logout(self) -> None:
        """Close the API session and free its seat on the Pi-hole."""
        if self._sid is None:
            return
        try:
            resp = self._send("DELETE", "/auth")
        finally:
            self._set_sid(None)
        # 401/404 mean the session was already gone, which is what we wanted.
        if not resp.ok and resp.status_code not in (401, 404, 410):
            raise error_from_response(resp)
        logger.debug("Logged out of %s", self.host)

    def close(self) -> None:
        """Log out (never raises) and close the HTTP connection pool."""
        try:
            self.logout()
        except PiHoleError as exc:
            logger.warning("Logout from %s failed: %s", self.host, exc)
        finally:
            self._session.close()

    def _set_sid(self, sid: Optional[str]) -> None:
        self._sid = sid
        if sid is None:
            self._session.headers.pop("X-FTL-SID", None)
        else:
            self._session.headers["X-FTL-SID"] = sid

    # -- HTTP plumbing ----------------------------------------------------

    def _send(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        try:
            return self._session.request(method, self.base_url + path, **kwargs)
        except requests.RequestException as exc:
            raise PiHoleConnectionError(
                f"Could not reach Pi-hole at {self.host}: {exc}"
            ) from exc

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Call any API endpoint, e.g. ``request("GET", "/stats/database/summary")``.

        ``path`` is relative to ``/api``. Logs in first if needed and, on a
        401, logs in again once and retries. Raises :class:`APIError`
        subclasses on HTTP errors.
        """
        if self.password is not None and self._sid is None:
            self.login()
        resp = self._send(method, path, **kwargs)
        if resp.status_code == 401 and self.password is not None:
            logger.debug("Session expired, logging in again")
            self.login()
            resp = self._send(method, path, **kwargs)
        if not resp.ok:
            raise error_from_response(resp)
        return resp

    def _json(self, method: str, path: str, **kwargs: Any) -> JSON:
        resp = self.request(method, path, **kwargs)
        if not resp.content:
            return {}
        data = resp.json()
        data.pop("took", None)
        return data

    # -- info and statistics ----------------------------------------------

    def version(self) -> JSON:
        """Versions of core, web, FTL and docker (local and latest remote)."""
        return self._json("GET", "/info/version")["version"]

    def summary(self) -> JSON:
        """Query, client and gravity counters (``queries``, ``clients``, ``gravity``)."""
        return self._json("GET", "/stats/summary")

    def gravity_last_update(self) -> Optional[datetime]:
        """When the gravity database was last rebuilt (UTC), or None if never."""
        ts = self.summary().get("gravity", {}).get("last_update")
        if not ts:
            return None
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    def top_domains(self, count: int = 10, blocked: bool = False) -> List[JSON]:
        """Most queried domains, or most blocked ones with ``blocked=True``."""
        params = {"count": count, "blocked": "true" if blocked else "false"}
        return self._json("GET", "/stats/top_domains", params=params)["domains"]

    def top_clients(self, count: int = 10, blocked: bool = False) -> List[JSON]:
        """Most active clients, or the ones with most blocked queries."""
        params = {"count": count, "blocked": "true" if blocked else "false"}
        return self._json("GET", "/stats/top_clients", params=params)["clients"]

    def recent_blocked(self, count: int = 1) -> List[str]:
        """The most recently blocked domains, newest first."""
        return self._json("GET", "/stats/recent_blocked", params={"count": count})[
            "blocked"
        ]

    def upstreams(self) -> List[JSON]:
        """Upstream DNS servers with their query counts."""
        return self._json("GET", "/stats/upstreams")["upstreams"]

    def query_types(self) -> JSON:
        """Query count per record type (A, AAAA, HTTPS, ...)."""
        return self._json("GET", "/stats/query_types")["types"]

    def cache_info(self) -> JSON:
        """DNS cache metrics (size, inserted, evicted, ...)."""
        return self._json("GET", "/info/metrics")["metrics"]["dns"]["cache"]

    def clients(self) -> List[JSON]:
        """Devices seen on the network, with their IPs and names."""
        return self._json("GET", "/network/devices")["devices"]

    def history(self) -> List[JSON]:
        """Total/blocked/cached/forwarded queries in 10-minute buckets."""
        return self._json("GET", "/history")["history"]

    def history_clients(self) -> JSON:
        """Per-client query counts in 10-minute buckets (``clients`` and ``history``)."""
        return self._json("GET", "/history/clients")

    def dns_port(self) -> int:
        """The port FTL answers DNS on."""
        return self._json("GET", "/config/dns/port")["config"]["dns"]["port"]

    # -- blocking ---------------------------------------------------------

    def blocking_status(self) -> JSON:
        """``{"blocking": "enabled" | "disabled" | "failed" | "unknown", "timer": ...}``."""
        return self._json("GET", "/dns/blocking")

    def enable(self) -> JSON:
        """Turn blocking on. Returns the new blocking status."""
        return self._set_blocking(True, None)

    def disable(self, seconds: Optional[int] = None) -> JSON:
        """Turn blocking off, for ``seconds`` or indefinitely when None or 0."""
        return self._set_blocking(False, seconds or None)

    def _set_blocking(self, blocking: bool, timer: Optional[int]) -> JSON:
        payload = {"blocking": blocking, "timer": timer}
        return self._json("POST", "/dns/blocking", json=payload)

    # -- allow / deny lists -----------------------------------------------

    def _add_domain(
        self, list_type: str, kind: str, domain: str, comment: Optional[str]
    ) -> JSON:
        payload: JSON = {"domain": domain}
        if comment is not None:
            payload["comment"] = comment
        return self._json("POST", f"/domains/{list_type}/{kind}", json=payload)

    def _remove_domain(self, list_type: str, kind: str, domain: str) -> None:
        self.request("DELETE", f"/domains/{list_type}/{kind}/{_quote(domain)}")

    def allow(self, domain: str, comment: Optional[str] = None) -> JSON:
        """Add an exact domain to the allow list."""
        return self._add_domain("allow", "exact", domain, comment)

    def remove_allow(self, domain: str) -> None:
        """Remove an exact domain from the allow list."""
        self._remove_domain("allow", "exact", domain)

    def allow_regex(self, pattern: str, comment: Optional[str] = None) -> JSON:
        """Add a regex to the allow list."""
        return self._add_domain("allow", "regex", pattern, comment)

    def remove_allow_regex(self, pattern: str) -> None:
        """Remove a regex from the allow list."""
        self._remove_domain("allow", "regex", pattern)

    def deny(self, domain: str, comment: Optional[str] = None) -> JSON:
        """Add an exact domain to the deny list."""
        return self._add_domain("deny", "exact", domain, comment)

    def remove_deny(self, domain: str) -> None:
        """Remove an exact domain from the deny list."""
        self._remove_domain("deny", "exact", domain)

    def deny_regex(self, pattern: str, comment: Optional[str] = None) -> JSON:
        """Add a regex to the deny list."""
        return self._add_domain("deny", "regex", pattern, comment)

    def remove_deny_regex(self, pattern: str) -> None:
        """Remove a regex from the deny list."""
        self._remove_domain("deny", "regex", pattern)

    # -- actions ----------------------------------------------------------

    def update_gravity(self, timeout: float = 600) -> str:
        """Rebuild the gravity database (``pihole -g``). Returns its log output.

        This can take minutes, so it has its own, longer ``timeout``.
        """
        return self.request("POST", "/action/gravity", timeout=timeout).text

    def restart_dns(self) -> None:
        """Restart the FTL DNS resolver."""
        self.request("POST", "/action/restartdns")
