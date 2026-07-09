from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import database.models  # noqa: F401
from database.base import Model


@pytest.fixture()
def session() -> Session:
    """Crée une base SQLite en mémoire, neuve pour chaque test."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Model.metadata.create_all(bind=engine)

    SessionTest = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with SessionTest() as session_test:
        yield session_test

    Model.metadata.drop_all(bind=engine)
    engine.dispose()
