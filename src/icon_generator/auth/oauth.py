"""OAuth provider configurations."""

from typing import Optional
from authlib.integrations.starlette_client import OAuth

from .config import auth_settings

# Create OAuth client
oauth = OAuth()


def configure_oauth():
    """
    Configure OAuth providers based on available credentials.

    Call this during app startup after environment is loaded.
    """
    if auth_settings.google_enabled:
        oauth.register(
            name="google",
            client_id=auth_settings.google_client_id,
            client_secret=auth_settings.google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    if auth_settings.github_enabled:
        oauth.register(
            name="github",
            client_id=auth_settings.github_client_id,
            client_secret=auth_settings.github_client_secret,
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url="https://github.com/login/oauth/access_token",
            api_base_url="https://api.github.com/",
            client_kwargs={"scope": "user:email"},
        )

    if auth_settings.apple_enabled:
        oauth.register(
            name="apple",
            client_id=auth_settings.apple_client_id,
            client_secret=auth_settings.apple_client_secret,
            authorize_url="https://appleid.apple.com/auth/authorize",
            access_token_url="https://appleid.apple.com/auth/token",
            client_kwargs={
                "scope": "name email",
                "response_mode": "form_post",
            },
        )


def get_oauth_client(provider: str) -> Optional[object]:
    """
    Get an OAuth client for the specified provider.

    Args:
        provider: The provider name ("google", "github", or "apple")

    Returns:
        OAuth client if configured, None otherwise
    """
    try:
        return getattr(oauth, provider, None)
    except AttributeError:
        return None


def get_available_providers() -> list[str]:
    """
    Get list of configured OAuth providers.

    Returns:
        List of provider names that are properly configured
    """
    providers = []
    if auth_settings.google_enabled:
        providers.append("google")
    if auth_settings.github_enabled:
        providers.append("github")
    if auth_settings.apple_enabled:
        providers.append("apple")
    return providers
