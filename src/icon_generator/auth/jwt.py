"""JWT token creation and verification."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from .config import auth_settings


class TokenError(Exception):
    """Raised when token operations fail."""

    pass


def create_access_token(
    user_id: uuid.UUID,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: The user's UUID
        email: The user's email
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=auth_settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    """
    Create a JWT refresh token.

    Args:
        user_id: The user's UUID

    Returns:
        Tuple of (token_string, expiration_datetime)
    """
    expires_delta = timedelta(days=auth_settings.refresh_token_expire_days)
    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # Unique token ID for revocation
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload,
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )

    return token, expire


def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        TokenError: If token is invalid, expired, or wrong type
    """
    try:
        payload = jwt.decode(
            token,
            auth_settings.jwt_secret_key,
            algorithms=[auth_settings.jwt_algorithm],
        )

        if payload.get("type") != expected_type:
            raise TokenError(f"Invalid token type. Expected {expected_type}")

        return payload

    except JWTError as e:
        raise TokenError(f"Invalid token: {str(e)}")


def create_password_reset_token(user_id: uuid.UUID, email: str) -> str:
    """
    Create a password reset token (short-lived).

    Args:
        user_id: The user's UUID
        email: The user's email

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        auth_settings.jwt_secret_key,
        algorithm=auth_settings.jwt_algorithm,
    )


def verify_password_reset_token(token: str) -> dict:
    """
    Verify a password reset token.

    Args:
        token: The reset token string

    Returns:
        Decoded token payload with user_id and email

    Raises:
        TokenError: If token is invalid or expired
    """
    return verify_token(token, expected_type="password_reset")
