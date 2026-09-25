"""Python client for the Pi-hole v6 REST API."""
import logging

from .client import PiHole
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PiHoleConnectionError,
    PiHoleError,
    RateLimitError,
)

__version__ = "1.0.0"

__all__ = [
    "PiHole",
    "PiHoleError",
    "PiHoleConnectionError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "__version__",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
