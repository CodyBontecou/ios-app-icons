"""Authentication module for the icon generator."""

from .config import auth_settings
from .password import verify_password, get_password_hash
from .jwt import create_access_token, create_refresh_token, verify_token
from .dependencies import get_current_user, require_auth

__all__ = [
    "auth_settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_current_user",
    "require_auth",
]
