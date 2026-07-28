from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models.models_participants import BulletinParticipation


class BulletinParticipationBD:
    """Service de persistance des bulletins de participation."""

    def __init__(self, session_bd: Session) -> None:
        self._session_bd = session_bd

    @staticmethod
    def _verifier_identifiant(
        identifiant: int,
        nom_parametre: str,
    ) -> None:
        if isinstance(identifiant, bool) or not isinstance(identifiant, int):
            raise TypeError(f"{nom_parametre} doit être un entier.")

        if identifiant <= 0:
            raise ValueError(
                f"{nom_parametre} doit être strictement positif."
            )

    def sauvegarder(
        self,
        bulletin: BulletinParticipation,
    ) -> BulletinParticipation:
        """Enregistre un bulletin ou ses modifications."""
        if not isinstance(
            bulletin,
            BulletinParticipation,
        ):
            raise TypeError(
                "bulletin doit être une instance "
                "de BulletinParticipation."
            )

        try:
            self._session_bd.add(bulletin)
            self._session_bd.commit()
            self._session_bd.refresh(bulletin)

            return bulletin

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def charger(
        self,
        bulletin_id: int,
    ) -> BulletinParticipation | None:
        """Charge un bulletin par sa clé primaire."""
        self._verifier_identifiant(
            bulletin_id,
            "bulletin_id",
        )

        try:
            return self._session_bd.get(
                BulletinParticipation,
                bulletin_id,
            )
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerParEleve(
        self,
        eleve_id: int,
    ) -> list[BulletinParticipation]:
        """
        Charge les bulletins associés à un élève.

        La requête utilise directement ``BulletinParticipation.eleve_id``
        lorsque cette clé étrangère existe. Si le bulletin est relié à un
        Participant ou à une Participation, le service tente une jointure
        par ``participant_id`` puis ``eleve_id``.
        """
        self._verifier_identifiant(
            eleve_id,
            "eleve_id",
        )

        if hasattr(BulletinParticipation, "eleve_id"):
            requete = select(BulletinParticipation).where(
                BulletinParticipation.eleve_id == eleve_id
            )

        elif hasattr(
            BulletinParticipation,
            "participant_id",
        ):
            participant_classe = self._obtenir_classe_participant()

            if not hasattr(participant_classe, "eleve_id"):
                raise AttributeError(
                    "Le modèle Participant ou Participation doit "
                    "définir l'attribut eleve_id."
                )

            requete = (
                select(BulletinParticipation)
                .join(
                    participant_classe,
                    BulletinParticipation.participant_id
                    == participant_classe.id,
                )
                .where(
                    participant_classe.eleve_id == eleve_id
                )
            )

        else:
            raise AttributeError(
                "BulletinParticipation doit définir eleve_id ou "
                "participant_id pour permettre chargerParEleve()."
            )

        if hasattr(BulletinParticipation, "id"):
            requete = requete.order_by(
                BulletinParticipation.id.asc()
            )

        try:
            return list(
                self._session_bd.scalars(requete).all()
            )
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    @staticmethod
    def _obtenir_classe_participant() -> type:
        """
        Retrouve la classe Participant ou Participation du modèle.

        Cette tolérance est temporaire : le projet doit finalement
        harmoniser ces deux noms.
        """
        try:
            from database.models.models_participants import Participant

            return Participant

        except ImportError:
            try:
                from database.models.models_participants import Participation

                return Participation

            except ImportError as exc:
                raise ImportError(
                    "Le module models_participants doit définir "
                    "Participant ou Participation."
                ) from exc