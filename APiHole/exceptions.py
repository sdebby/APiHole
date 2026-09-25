"""Exceptions raised by the APiHole client."""
from __future__ import annotations

from typing import Optional

import requests


class PiHoleError(Exception):
    """Base class for every error raised by APiHole."""


class PiHoleConnectionError(PiHoleError):
    """The Pi-hole could not be reached (DNS, refused connection, timeout, TLS)."""


class APIError(PiHoleError):
    """The Pi-hole answered with an HTTP error.

    ``key``, ``message`` and ``hint`` come from the v6 error body
    ``{"error": {"key": ..., "message": ..., "hint": ...}}`` when present.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        key: Optional[str] = None,
        hint: Optional[str] = None,
        response: Optional[requests.Response] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.key = key
        self.hint = hint
        self.response = response

    def __str__(self) -> str:
        text = self.message
        if self.status_code is not None:
            text = f"[{self.status_code}] {text}"
        if self.hint:
            text = f"{text} ({self.hint})"
        return text


class AuthenticationError(APIError):
    """HTTP 401: wrong password, missing TOTP, or the session expired."""


class NotFoundError(APIError):
    """HTTP 404: the endpoint or item does not exist."""


class RateLimitError(APIError):
    """HTTP 429: too many requests or no free API session seats."""


_STATUS_TO_ERROR = {
    401: AuthenticationError,
    404: NotFoundError,
    429: RateLimitError,
}


def error_from_response(response: requests.Response) -> APIError:
    """Build the matching :class:`APIError` subclass from a failed response."""
    key = hint = None
    message = response.reason or f"HTTP {response.status_code}"
    try:
        error = response.json().get("error") or {}
    except ValueError:
        error = {}
    if isinstance(error, dict):
        key = error.get("key")
        hint = error.get("hint")
        message = error.get("message") or message
    cls = _STATUS_TO_ERROR.get(response.status_code, APIError)
    return cls(
        message,
        status_code=response.status_code,
        key=key,
        hint=hint,
        response=response,
    )
