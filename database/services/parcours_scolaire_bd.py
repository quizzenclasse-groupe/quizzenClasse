from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models.models_participants import Eleve
from database.models.models_scolaire import Etablissement, Niveau
from database.models.models_utilisateurs import Enseignant


class ParcoursScolaireBD:
    """
    Service de persistance de l'environnement scolaire.

    Il centralise les lectures et les écritures concernant les
    établissements rattachés à un enseignant, les niveaux scolaires
    et les élèves.
    """

    def __init__(self, session_bd: Session) -> None:
        """
        Initialise le service avec une session SQLAlchemy active.
        """
        self._session_bd = session_bd

    @staticmethod
    def _verifier_identifiant(
        identifiant: int,
        nom_parametre: str,
    ) -> None:
        """Vérifie qu'un identifiant est un entier strictement positif."""
        if isinstance(identifiant, bool) or not isinstance(identifiant, int):
            raise TypeError(f"{nom_parametre} doit être un entier.")

        if identifiant <= 0:
            raise ValueError(
                f"{nom_parametre} doit être strictement positif."
            )

    @staticmethod
    def _trier_par_identifiant(
        objets: Sequence[object],
    ) -> list[object]:
        """Retourne une liste triée lorsque les objets possèdent un id."""
        return sorted(
            objets,
            key=lambda objet: getattr(objet, "id", 0) or 0,
        )

    def _charger_enseignant(
        self,
        enseignant_id: int,
    ) -> Enseignant:
        """Charge un enseignant et signale clairement son absence."""
        self._verifier_identifiant(
            enseignant_id,
            "enseignant_id",
        )

        enseignant = self._session_bd.get(
            Enseignant,
            enseignant_id,
        )

        if enseignant is None:
            raise ValueError(
                "Aucun enseignant ne correspond à l'identifiant "
                f"{enseignant_id}."
            )

        return enseignant

    def chargerEtablissementsParEnseignant(
        self,
        enseignant_id: int,
    ) -> list[Etablissement]:
        """
        Charge les établissements rattachés à un enseignant.

        Le code accepte les noms de relations ``etablissements`` et
        ``etablissement_liste``. Si le modèle utilise une clé étrangère
        ``Etablissement.enseignant_id``, celle-ci est utilisée comme solution
        de repli.
        """
        enseignant = self._charger_enseignant(enseignant_id)

        for nom_relation in (
            "etablissements",
            "etablissement_liste",
        ):
            relation = getattr(
                enseignant,
                nom_relation,
                None,
            )

            if relation is not None:
                return list(
                    self._trier_par_identifiant(
                        list(relation)
                    )
                )

        etablissement_unique = getattr(
            enseignant,
            "etablissement",
            None,
        )

        if etablissement_unique is not None:
            return [etablissement_unique]

        if hasattr(Etablissement, "enseignant_id"):
            requete = (
                select(Etablissement)
                .where(
                    Etablissement.enseignant_id
                    == enseignant_id
                )
                .order_by(Etablissement.id.asc())
            )

            try:
                return list(
                    self._session_bd.scalars(requete).all()
                )
            except SQLAlchemyError:
                self._session_bd.rollback()
                raise

        raise AttributeError(
            "Le modèle doit définir une relation entre Enseignant et "
            "Etablissement : Enseignant.etablissements, "
            "Enseignant.etablissement_liste, Enseignant.etablissement "
            "ou Etablissement.enseignant_id."
        )

    def sauvegarderEtablissement(
        self,
        enseignant_id: int,
        etablissement: Etablissement,
    ) -> Etablissement:
        """
        Enregistre un établissement et le rattache à un enseignant.
        """
        if not isinstance(etablissement, Etablissement):
            raise TypeError(
                "etablissement doit être une instance d'Etablissement."
            )

        enseignant = self._charger_enseignant(enseignant_id)
        rattachement_effectue = False

        if hasattr(etablissement, "enseignant_id"):
            etablissement.enseignant_id = enseignant_id
            rattachement_effectue = True

        for nom_relation in (
            "etablissements",
            "etablissement_liste",
        ):
            relation = getattr(
                enseignant,
                nom_relation,
                None,
            )

            if relation is not None:
                if etablissement not in relation:
                    relation.append(etablissement)
                rattachement_effectue = True
                break

        if (
            not rattachement_effectue
            and hasattr(enseignant, "etablissement")
        ):
            enseignant.etablissement = etablissement
            rattachement_effectue = True

        if not rattachement_effectue:
            raise AttributeError(
                "Impossible de rattacher l'établissement : crée une relation "
                "SQLAlchemy entre Enseignant et Etablissement."
            )

        try:
            self._session_bd.add(etablissement)
            self._session_bd.add(enseignant)
            self._session_bd.commit()
            self._session_bd.refresh(etablissement)

            return etablissement

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerNiveauxParEnseignant(
        self,
        enseignant_id: int,
    ) -> list[Niveau]:
        """Charge tous les niveaux scolaires d'un enseignant."""
        self._verifier_identifiant(
            enseignant_id,
            "enseignant_id",
        )

        requete = (
            select(Niveau)
            .where(
                Niveau.enseignant_id
                == enseignant_id
            )
            .order_by(Niveau.id.asc())
        )

        try:
            return list(
                self._session_bd.scalars(requete).all()
            )
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def sauvegarderNiveau(
        self,
        niveau: Niveau,
    ) -> Niveau:
        """Enregistre un nouveau niveau ou ses modifications."""
        if not isinstance(niveau, Niveau):
            raise TypeError(
                "niveau doit être une instance de Niveau."
            )

        try:
            self._session_bd.add(niveau)
            self._session_bd.commit()
            self._session_bd.refresh(niveau)

            return niveau

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerElevesParNiv(
        self,
        niveau_id: int,
    ) -> list[Eleve]:
        """Charge les élèves rattachés à un niveau scolaire."""
        self._verifier_identifiant(
            niveau_id,
            "niveau_id",
        )

        requete = (
            select(Eleve)
            .where(
                Eleve.niveau_scolaire_id
                == niveau_id
            )
            .order_by(Eleve.id.asc())
        )

        try:
            return list(
                self._session_bd.scalars(requete).all()
            )
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def supprimerElevesParNiv(
        self,
        niveau_id: int,
    ) -> int:
        """
        Supprime tous les élèves d'un niveau.

        Returns:
            Le nombre de lignes supprimées lorsque le pilote le fournit.
        """
        self._verifier_identifiant(
            niveau_id,
            "niveau_id",
        )

        requete = delete(Eleve).where(
            Eleve.niveau_scolaire_id == niveau_id
        )

        try:
            resultat = self._session_bd.execute(requete)
            self._session_bd.commit()

            return int(resultat.rowcount or 0)

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def sauvegarderEleve(
        self,
        eleve: Eleve,
    ) -> Eleve:
        """Enregistre un nouvel élève ou ses modifications."""
        if not isinstance(eleve, Eleve):
            raise TypeError(
                "eleve doit être une instance d'Eleve."
            )

        try:
            self._session_bd.add(eleve)
            self._session_bd.commit()
            self._session_bd.refresh(eleve)

            return eleve

        except SQLAlchemyError:
            self._session_bd.rollback()
            raise

    def chargerEleve(
        self,
        eleve_id: int,
    ) -> Eleve | None:
        """Charge un élève par sa clé primaire."""
        self._verifier_identifiant(
            eleve_id,
            "eleve_id",
        )

        try:
            return self._session_bd.get(Eleve, eleve_id)
        except SQLAlchemyError:
            self._session_bd.rollback()
            raise
