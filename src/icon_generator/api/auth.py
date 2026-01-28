"""Authentication routes for the icon generator API."""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.config import auth_settings
from ..auth.jwt import (
    TokenError,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    verify_password_reset_token,
    verify_token,
)
from ..auth.oauth import configure_oauth, get_available_providers, get_oauth_client, oauth
from ..auth.password import get_password_hash, validate_password_strength, verify_password
from ..auth.dependencies import CurrentUser
from ..db.database import get_async_session
from ..db.models import RefreshToken, User
from .schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    OAuthProviderInfo,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


async def create_tokens_for_user(
    user: User,
    session: AsyncSession,
) -> TokenResponse:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(user.id, user.email)
    refresh_token, expires_at = create_refresh_token(user.id)

    # Store hashed refresh token in database
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    )
    session.add(token_record)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=auth_settings.access_token_expire_minutes * 60,
    )


# --- Email/Password Authentication ---


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid registration data"},
        409: {"description": "Email already registered"},
    },
)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """
    Register a new user with email and password.

    Returns access and refresh tokens on successful registration.
    """
    # TODO: Add rate limiting to prevent abuse

    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Check if email already exists
    result = await session.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return await create_tokens_for_user(user, session)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """
    Login with email and password.

    Returns access and refresh tokens on successful authentication.
    """
    # TODO: Add rate limiting to prevent brute force attacks

    # Find user by email
    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Verify user exists and has a password (not OAuth-only)
    if user is None or user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return await create_tokens_for_user(user, session)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    request: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """
    Exchange a refresh token for new access and refresh tokens.

    The old refresh token is invalidated after use.
    """
    try:
        payload = verify_token(request.refresh_token, expected_type="refresh")
        user_id = uuid.UUID(payload["sub"])
    except (TokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    # Find and validate the refresh token in database
    token_hash = hash_token(request.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    token_record = result.scalar_one_or_none()

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Revoke the old refresh token
    token_record.revoked = True
    await session.commit()

    # Get the user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return await create_tokens_for_user(user, session)


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        401: {"description": "Invalid refresh token"},
    },
)
async def logout(
    request: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MessageResponse:
    """
    Logout by invalidating the refresh token.
    """
    token_hash = hash_token(request.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token_record = result.scalar_one_or_none()

    if token_record:
        token_record.revoked = True
        await session.commit()

    return MessageResponse(message="Logged out successfully")


# --- Password Reset ---


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MessageResponse:
    """
    Request a password reset email.

    Always returns success to prevent email enumeration.
    """
    # TODO: Add rate limiting to prevent abuse

    result = await session.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if user:
        # Create reset token
        reset_token = create_password_reset_token(user.id, user.email)

        # TODO: Send email with reset link
        # For now, log the token (remove in production)
        print(f"Password reset token for {user.email}: {reset_token}")

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    responses={
        400: {"description": "Invalid or expired reset token"},
    },
)
async def reset_password(
    request: ResetPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MessageResponse:
    """
    Reset password using a reset token.
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        payload = verify_password_reset_token(request.token)
        user_id = uuid.UUID(payload["sub"])
    except (TokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update user password
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    user.password_hash = get_password_hash(request.new_password)
    await session.commit()

    # Revoke all existing refresh tokens for this user
    await session.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.user_id == user_id)
        .values(revoked=True)
    )
    await session.commit()

    return MessageResponse(message="Password reset successfully")


# --- OAuth ---


@router.get("/oauth/providers")
async def get_oauth_providers() -> list[OAuthProviderInfo]:
    """
    Get list of available OAuth providers.
    """
    providers = []
    for provider in ["google", "github", "apple"]:
        enabled = provider in get_available_providers()
        providers.append(
            OAuthProviderInfo(
                provider=provider,
                enabled=enabled,
                authorize_url=f"/auth/oauth/{provider}" if enabled else None,
            )
        )
    return providers


@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Redirect to OAuth provider for authentication.
    """
    if provider not in get_available_providers():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' is not configured",
        )

    client = get_oauth_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth client for '{provider}'",
        )

    redirect_uri = f"{auth_settings.backend_url}/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """
    Handle OAuth callback and create/login user.
    """
    if provider not in get_available_providers():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' is not configured",
        )

    client = get_oauth_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth client for '{provider}'",
        )

    try:
        token = await client.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {str(e)}",
        )

    # Get user info based on provider
    if provider == "google":
        user_info = token.get("userinfo")
        if user_info is None:
            user_info = await client.userinfo(token=token)
        email = user_info.get("email")
        name = user_info.get("name")
        avatar_url = user_info.get("picture")

    elif provider == "github":
        resp = await client.get("user", token=token)
        user_data = resp.json()
        email = user_data.get("email")
        name = user_data.get("name") or user_data.get("login")
        avatar_url = user_data.get("avatar_url")

        # GitHub may not return email in user endpoint
        if not email:
            resp = await client.get("user/emails", token=token)
            emails = resp.json()
            primary_email = next((e for e in emails if e.get("primary")), None)
            if primary_email:
                email = primary_email.get("email")

    elif provider == "apple":
        # Apple provides user info in the ID token
        id_token = token.get("id_token")
        user_info = await client.parse_id_token(token, None)
        email = user_info.get("email")
        name = None  # Apple only provides name on first authorization
        avatar_url = None

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get email from OAuth provider",
        )

    # Find or create user
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        # Create new user
        user = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            email_verified=True,  # OAuth emails are verified
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update user info if not set
        updated = False
        if name and not user.name:
            user.name = name
            updated = True
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            updated = True
        if not user.email_verified:
            user.email_verified = True
            updated = True
        if updated:
            await session.commit()

    # Create tokens
    tokens = await create_tokens_for_user(user, session)

    # Redirect to frontend with tokens
    redirect_url = (
        f"{auth_settings.frontend_url}/auth/callback"
        f"?access_token={tokens.access_token}"
        f"&refresh_token={tokens.refresh_token}"
        f"&expires_in={tokens.expires_in}"
    )

    return RedirectResponse(url=redirect_url)


# --- User Info ---


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: CurrentUser) -> UserResponse:
    """
    Get the current authenticated user's information.
    """
    return UserResponse.model_validate(user)
