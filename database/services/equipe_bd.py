from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models.models_participants import Equipe


class EquipeBD:
    """Service de persistance des groupes d'élèves."""

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
        equipe: Equipe,
    ) -> Equipe:
        """Enregistre une nouvelle equipe ou ses modifications."""
        if not isinstance(equipe, Equipe):
            raise TypeError(
                "equipe doit être une instance de Equipe."
            )

        try:
            self._session_bd.add(equipe)
            self._session_bd.commit()
            self._session_bd.refresh(equipe)

            return equipe

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def charger(
        self,
        groupe_id: int,
    ) -> Equipe | None:
        """Charge une équipe par sa clé primaire."""
        self._verifier_identifiant(
            groupe_id,
            "groupe_id",
        )

        try:
            return self._session_bd.get(Equipe, groupe_id)
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerTous(self) -> list[Equipe]:
        """Charge toutes les équipes enregistrées."""
        requete = select(Equipe).order_by(Equipe.id.asc())

        try:
            return list(
                self._session_bd.scalars(requete).all()
            )
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def supprimer(
        self,
        equipe: Equipe,
    ) -> None:
        """Supprime une equipe existante."""
        if not isinstance(equipe, Equipe):
            raise TypeError(
                "équipe doit être une instance de Equipe."
            )

        try:
            self._session_bd.delete(equipe)
            self._session_bd.commit()

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise