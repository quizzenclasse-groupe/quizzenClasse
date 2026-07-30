# api/repositories/cours_repository.py
"""Accès base de données pour l'entité Cours."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.repositories.base import BaseRepository
from database.models.models_evaluation import Cours


class CoursRepository(BaseRepository[Cours]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Cours)

    def par_enseignant(self, enseignant_id: int) -> list[Cours]:
        return list(
            self.session.execute(
                select(Cours).where(Cours.enseignant_id == enseignant_id)
            ).scalars().all()
        )
