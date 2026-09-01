"""LAN access control.

`lan_mode` and `lan_token` have existed in config.py since the settings module
was written, and until now were referenced NOWHERE else in the codebase. They
read like an access control and enforced nothing -- every endpoint was open,
with the only `Depends()` in api.py being the database session.

That was survivable only because `host` defaults to 127.0.0.1, so the API was
reachable from the local machine alone. Anything that binds 0.0.0.0 -- a
container, most obviously, where the published port does nothing otherwise --
turns six unauthenticated CRUD endpoints into a network service.

So the fields now do what they claim.

FAILS CLOSED. If lan_mode is on and no token is configured, every request is
refused rather than allowed through: a half-configured deployment must not be
an open one.

Constant-time comparison, because a naive `==` on a shared secret leaks its
prefix to anyone who can time responses.
"""

import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

from tick_task.config import settings

_SCHEME = "Bearer"


async def require_lan_token(authorization: Optional[str] = Header(None)) -> None:
    """Reject requests without a valid LAN token, when lan_mode is enabled.

    No-op when lan_mode is off, which keeps the default loopback-only posture
    exactly as it was.
    """
    if not settings.lan_mode:
        return

    if not settings.lan_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="lan_mode is enabled but lan_token is not configured",
        )

    expected = f"{_SCHEME} {settings.lan_token}"
    supplied = authorization or ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing LAN token",
            headers={"WWW-Authenticate": _SCHEME},
        )
