"""Database initialization hooks for FastAPI."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .database import init_db, close_db


@asynccontextmanager
async def db_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager for database initialization.

    Usage:
        app = FastAPI(lifespan=db_lifespan)
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


async def on_startup() -> None:
    """Database startup hook for FastAPI.

    Usage with add_event_handler:
        app.add_event_handler("startup", on_startup)
    """
    await init_db()


async def on_shutdown() -> None:
    """Database shutdown hook for FastAPI.

    Usage with add_event_handler:
        app.add_event_handler("shutdown", on_shutdown)
    """
    await close_db()
