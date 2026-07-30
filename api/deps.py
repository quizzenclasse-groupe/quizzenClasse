# api/deps.py
"""
Dépendances FastAPI transversales (indépendantes d'un domaine métier
particulier). Pour l'instant : uniquement l'accès à la base de données.
"""

from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session as OrmSession

from database.engine import Session as SessionFactory


def get_db() -> Generator[OrmSession, None, None]:
    """
    Fournit une session SQLAlchemy pour la durée d'une requête HTTP,
    puis la ferme systématiquement (même en cas d'exception), selon le
    pattern standard "yield" des dépendances FastAPI.

    On réutilise directement la fabrique de sessions déjà définie dans
    `database/engine.py` (celle utilisée par le programme console dans
    `main.py`) : aucune configuration de connexion n'est dupliquée.
    """
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()
