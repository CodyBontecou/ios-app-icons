"""Authentication configuration settings."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthSettings:
    """Authentication configuration from environment variables."""

    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-min-32-chars")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # OAuth - Google
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")

    # OAuth - GitHub
    github_client_id: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")

    # OAuth - Apple
    apple_client_id: Optional[str] = os.getenv("APPLE_CLIENT_ID")
    apple_client_secret: Optional[str] = os.getenv("APPLE_CLIENT_SECRET")
    apple_team_id: Optional[str] = os.getenv("APPLE_TEAM_ID")
    apple_key_id: Optional[str] = os.getenv("APPLE_KEY_ID")

    # App URLs
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    @property
    def google_enabled(self) -> bool:
        """Check if Google OAuth is configured."""
        return bool(self.google_client_id and self.google_client_secret)

    @property
    def github_enabled(self) -> bool:
        """Check if GitHub OAuth is configured."""
        return bool(self.github_client_id and self.github_client_secret)

    @property
    def apple_enabled(self) -> bool:
        """Check if Apple OAuth is configured."""
        return bool(
            self.apple_client_id
            and self.apple_client_secret
            and self.apple_team_id
            and self.apple_key_id
        )


# Global settings instance
auth_settings = AuthSettings()
