"""Database session management using SQLAlchemy 2.0 style."""

from contextlib import contextmanager

from typing import Iterator

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_engine(str(settings.database_url), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_db() -> Iterator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
