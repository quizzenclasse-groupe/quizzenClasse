# tests/conftest.py
# *******************************************************
# Nom ......... : conftest.py
# Rôle ........ : Définit les fixtures communes à la suite de
#                 tests Pytest. Crée pour chaque test une base
#                 de données SQLite en mémoire, initialise les
#                 tables SQLAlchemy et fournit une session de
#                 test isolée.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile tests/conftest.py
# Usage ....... : Fichier chargé automatiquement par Pytest :
#                 python -m pytest -q
# *******************************************************
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
