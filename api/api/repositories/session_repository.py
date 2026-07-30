# api/repositories/session_repository.py
# Rôle : Accès à la base de données pour SessionQuestionnaire, Participation et Rapport.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.repositories.base import BaseRepository
from database.models.models_evaluation import SessionQuestionnaire
from database.models.models_participants import Participation


class SessionQuestionnaireRepository(BaseRepository[SessionQuestionnaire]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, SessionQuestionnaire)

    def par_questionnaire(self, questionnaire_id: int) -> list[SessionQuestionnaire]:
        return list(
            self.session.execute(
                select(SessionQuestionnaire).where(
                    SessionQuestionnaire.questionnaire_id == questionnaire_id
                )
            ).scalars().all()
        )


class ParticipationRepository(BaseRepository[Participation]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Participation)

    def par_session(self, session_id: int) -> list[Participation]:
        return list(
            self.session.execute(
                select(Participation).where(
                    Participation.session_questionnaire_id == session_id
                )
            ).scalars().all()
        )

    def existe_deja(self, session_id: int, participant_id: int) -> bool:
        """Évite d'inscrire deux fois le même participant à la même session."""
        return (
            self.session.execute(
                select(Participation).where(
                    Participation.session_questionnaire_id == session_id,
                    Participation.participant_id == participant_id,
                )
            ).scalar_one_or_none()
            is not None
        )
