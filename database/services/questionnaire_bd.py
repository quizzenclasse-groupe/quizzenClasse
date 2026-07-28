from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from database.models.models_evaluation import (
        Questionnaire,
        Question,

    )

class QuestionnaireBD:
    """
    Service chargé de la persistance des questionnaires.

    La session SQLAlchemy est fournie lors de l'instanciation du service.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialise le service de persistance.

        Args:
            session: session SQLAlchemy utilisée pour les requêtes
                     et les transactions.
        """
        self.session = session

    def sauvegarder(
        self,
        questionnaire: Questionnaire,
    ) -> Questionnaire:
        """
        Enregistre un nouveau questionnaire ou sauvegarde ses modifications.

        Les questions et les propositions liées sont enregistrées par
        SQLAlchemy si les relations du modèle utilisent une cascade adaptée.

        Args:
            questionnaire: questionnaire à enregistrer.

        Returns:
            Le questionnaire sauvegardé.

        Raises:
            SQLAlchemyError: lorsqu'une erreur survient pendant la transaction.
        """
        try:
            self.session.add(questionnaire)
            self.session.commit()
            self.session.refresh(questionnaire)

            return questionnaire

        except SQLAlchemyError:
            self.session.rollback()
            raise

    def charger(
        self,
        questionnaire_id: int,
    ) -> Questionnaire | None:
        """
        Charge un questionnaire à partir de son identifiant.

        Les questions, les propositions et l'auteur sont chargés avec
        le questionnaire afin de pouvoir être utilisés immédiatement.

        Args:
            questionnaire_id: identifiant du questionnaire recherché.

        Returns:
            Le questionnaire correspondant ou None.
        """
        requete = (
            select(Questionnaire)
            .options(
                selectinload(Questionnaire.questions)
                .selectinload(Question.propositions),
                selectinload(Questionnaire.auteur),
            )
            .where(Questionnaire.id == questionnaire_id)
        )

        return self.session.scalar(requete)

    def chargerParEnseignant(
        self,
        enseignant_id: int,
    ) -> list[Questionnaire]:
        """
        Charge les questionnaires appartenant à un enseignant.

        Args:
            enseignant_id: identifiant de l'enseignant.

        Returns:
            La liste de ses questionnaires.
        """
        requete = (
            select(Questionnaire)
            .options(
                selectinload(Questionnaire.questions)
                .selectinload(Question.propositions),
                selectinload(Questionnaire.auteur),
            )
            .where(Questionnaire.auteur_id == enseignant_id)
            .order_by(Questionnaire.id)
        )

        return list(self.session.scalars(requete).all())