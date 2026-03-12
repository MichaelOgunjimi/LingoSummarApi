from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

# ── Database session dependency ───────────────────────────
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ── User UID from header ─────────────────────────────────
async def get_user_uid(x_user_uid: str = Header(default=None)) -> str | None:
    """Extract the Firebase UID from the X-User-UID header."""
    return x_user_uid


async def require_user_uid(x_user_uid: str = Header(default=None)) -> str:
    """Same as above, but raises 401 if missing."""
    if not x_user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-UID header is required",
        )
    return x_user_uid


UserUIDDep = Annotated[str | None, Depends(get_user_uid)]
RequiredUserUIDDep = Annotated[str, Depends(require_user_uid)]
