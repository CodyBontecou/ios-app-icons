"""API request/response schemas."""

from .auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    OAuthProviderInfo,
    MessageResponse,
    AuthErrorResponse,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "RefreshRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "OAuthProviderInfo",
    "MessageResponse",
    "AuthErrorResponse",
]
