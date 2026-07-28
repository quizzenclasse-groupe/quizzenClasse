from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models.models_evaluation import (
    Participant,
    RapportSession,
    SessionQuestionnaire,
)

from database.models.models_evaluation import (
    Questionnaire,
    RapportSession,
    SessionQuestionnaire,
)

class SessionQuestionnaireBD:
    """
    Service de persistance des sessions de questionnaire,
    de leurs participants et des rapports associés.

    Une instance de sqlalchemy.orm.Session est injectée dans le constructeur.
    Le service ne crée donc pas lui-même la connexion à la base de données.
    """

    def __init__(self, session_bd: Session) -> None:
        """
        Initialise le service avec une session SQLAlchemy active.

        Args:
            session_bd: session SQLAlchemy utilisée pour les lectures,
                les insertions et les mises à jour.

        Raises:
            TypeError: si l'objet fourni n'est pas une Session SQLAlchemy.
        """
        if not isinstance(session_bd, Session):
            raise TypeError(
                "session_bd doit être une instance de sqlalchemy.orm.Session."
            )

        self._session_bd = session_bd

    @staticmethod
    def _verifier_identifiant(
        identifiant: int,
        nom_parametre: str,
    ) -> None:
        """
        Vérifie qu'un identifiant est un entier strictement positif.
        """
        if isinstance(identifiant, bool) or not isinstance(identifiant, int):
            raise TypeError(
                f"{nom_parametre} doit être un entier."
            )

        if identifiant <= 0:
            raise ValueError(
                f"{nom_parametre} doit être strictement positif."
            )

    def chargerParEnseignant(
        self,
        enseignant_id: int,
    ) -> list[SessionQuestionnaire]:
        if enseignant_id <= 0:
            raise ValueError(
                "L'identifiant de l'enseignant doit être positif."
            )

        requete = (
            select(SessionQuestionnaire)
            .join(SessionQuestionnaire.questionnaire)
            .where(
                Questionnaire.enseignant_id == enseignant_id
            )
            .order_by(SessionQuestionnaire.id)
        )

        return list(
            self.session.scalars(requete).all()
        )


    def sauvegarder(
        self,
        session: SessionQuestionnaire,
    ) -> SessionQuestionnaire:
        """
        Enregistre une nouvelle session ou sauvegarde ses modifications.

        Session.add() convient aussi bien à une nouvelle instance qu'à une
        instance persistante déjà rattachée à cette session SQLAlchemy.

        Args:
            session: session de questionnaire à enregistrer.

        Returns:
            L'objet SessionQuestionnaire enregistré et actualisé.

        Raises:
            TypeError: si l'objet fourni n'est pas une SessionQuestionnaire.
            SQLAlchemyError: si l'enregistrement échoue.
        """
        if not isinstance(session, SessionQuestionnaire):
            raise TypeError(
                "session doit être une instance de SessionQuestionnaire."
            )

        try:
            self._session_bd.add(session)
            self._session_bd.commit()
            self._session_bd.refresh(session)

            return session

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerParticipantsParSession(
        self,
        session_id: int,
    ) -> list[Participant]:
        """
        Charge les participants rattachés à une session de questionnaire.

        Args:
            session_id: identifiant de la session concernée.

        Returns:
            La liste des participants, triée par identifiant croissant.
            Une liste vide est retournée si aucun participant n'est rattaché
            à cette session.

        Raises:
            TypeError: si l'identifiant n'est pas un entier.
            ValueError: si l'identifiant n'est pas strictement positif.
            SQLAlchemyError: si la lecture dans la base échoue.
        """
        self._verifier_identifiant(
            session_id,
            "session_id",
        )

        requete = (
            select(Participant)
            .where(
                Participant.session_questionnaire_id == session_id
            )
            .order_by(Participant.id.asc())
        )

        try:
            resultat = self._session_bd.scalars(requete)
            return list(resultat.all())

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def sauvegarderRapport(
        self,
        rapport: RapportSession,
    ) -> RapportSession:
        """
        Enregistre un rapport de session ou sauvegarde ses modifications.

        Args:
            rapport: rapport à enregistrer.

        Returns:
            L'objet RapportSession enregistré et actualisé.

        Raises:
            TypeError: si l'objet fourni n'est pas un RapportSession.
            SQLAlchemyError: si l'enregistrement échoue.
        """
        if not isinstance(rapport, RapportSession):
            raise TypeError(
                "rapport doit être une instance de RapportSession."
            )

        try:
            self._session_bd.add(rapport)
            self._session_bd.commit()
            self._session_bd.refresh(rapport)

            return rapport

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise