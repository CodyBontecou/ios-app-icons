"""FastAPI authentication dependencies."""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_async_session
from ..db.models import User
from .jwt import TokenError, verify_token

# Bearer token security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Optional[User]:
    """
    Get the current authenticated user from the JWT token.

    This dependency is optional - returns None if no valid token is provided.
    Use require_auth for endpoints that require authentication.

    Args:
        credentials: Bearer token credentials
        session: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        payload = verify_token(credentials.credentials, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
    except (TokenError, ValueError):
        return None

    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def require_auth(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """
    Require a valid authenticated user.

    Use this dependency for protected endpoints.

    Args:
        credentials: Bearer token credentials
        session: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(credentials.credentials, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
    except (TokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Type alias for use in route signatures
CurrentUser = Annotated[User, Depends(require_auth)]
OptionalUser = Annotated[Optional[User], Depends(get_current_user)]
