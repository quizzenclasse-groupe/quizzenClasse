# api/repositories/questionnaire_repository.py
"""Accès base de données pour Questionnaire, Question et Proposition."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.repositories.base import BaseRepository
from database.models.models_evaluation import Proposition, Question, Questionnaire


class QuestionnaireRepository(BaseRepository[Questionnaire]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Questionnaire)

    def par_auteur(self, auteur_id: int) -> list[Questionnaire]:
        return list(
            self.session.execute(
                select(Questionnaire).where(Questionnaire.auteur_id == auteur_id)
            ).scalars().all()
        )


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Question)


class PropositionRepository(BaseRepository[Proposition]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Proposition)
