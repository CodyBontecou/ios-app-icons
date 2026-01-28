"""Database module for icon generator."""

from .database import (
    async_engine,
    async_session_factory,
    get_async_session,
    init_db,
    close_db,
)
from .models import (
    Base,
    User,
    RefreshToken,
    Job,
    Icon,
    Subscription,
    Usage,
    JobStatus,
    PlanTier,
    SubscriptionStatus,
)
from .init import (
    db_lifespan,
    on_startup,
    on_shutdown,
)

__all__ = [
    # Database
    "async_engine",
    "async_session_factory",
    "get_async_session",
    "init_db",
    "close_db",
    # FastAPI hooks
    "db_lifespan",
    "on_startup",
    "on_shutdown",
    # Models
    "Base",
    "User",
    "RefreshToken",
    "Job",
    "Icon",
    "Subscription",
    "Usage",
    # Enums
    "JobStatus",
    "PlanTier",
    "SubscriptionStatus",
]
