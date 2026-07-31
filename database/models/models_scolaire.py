# database/models/models_scolaire.py
# *******************************************************
# Nom ......... : models_scolaire.py
# Rôle ........ : Définit les modèles ORM représentant les
#                 établissements et les niveaux scolaires,
#                 ainsi que les fonctions de chargement et de
#                 recherche des établissements.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/models/models_scolaire.py
# Usage ....... : Importer les modèles nécessaires, par exemple :
#                 from database.models.models_scolaire \
#                 import Etablissement, Niveau
# *******************************************************
from __future__ import annotations

import csv
import unicodedata
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Model
from database.tables_association import niveau_eleve

if TYPE_CHECKING:
    from database.models.models_participants import Eleve
    from database.models.models_utilisateurs import Enseignant

class Etablissement(Model):
    __tablename__ = "etablissement"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nom_etablissement: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    statut_public_prive: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    adresse_1: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    adresse_2: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    adresse_3: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    code_departement: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )

    nom_departement: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    type_etablissement: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="etablissement",
    )

    code_uai: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    nom_academie: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    code_postal: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    __mapper_args__ = {
        "polymorphic_on": type_etablissement,
        "polymorphic_identity": "etablissement",
    }

    def getId(self) -> int:
        return self.id

    def getNom(self) -> str:
        return self.nom_etablissement

    def getCodeUai(self) -> str | None:
        return self.code_uai

    def getNomAcademie(self) -> str | None:
        return self.nom_academie

    def getCodePostal(self) -> str | None:
        return self.code_postal


class Niveau(Model):
    __tablename__ = "niveau"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nom_niveau: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    effectif: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    etablissement_id: Mapped[int] = mapped_column(
        ForeignKey("etablissement.id"),
        nullable=False,
    )

    enseignant_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    etablissement: Mapped["Etablissement"] = relationship()

    enseignant: Mapped["Enseignant"] = relationship()

    eleves: Mapped[list["Eleve"]] = relationship(
        secondary=niveau_eleve,
        back_populates="niveaux",
    )

    def getId(self) -> int:
        return self.id

    def getEtablissementId(self) -> int:
        return self.etablissement_id

    def getEnseignantId(self) -> int:
        return self.enseignant_id

    def getNom(self) -> str:
        return self.nom_niveau

    def getEleveListe(self) -> list["Eleve"]:
        return list(self.eleves)

    def setNom(self, nom: str) -> None:
        nom = nom.strip()

        if not nom:
            raise ValueError(
                "Le nom du niveau scolaire ne peut pas être vide."
            )

        self.nom_niveau = nom

    def ajouterEleve(self, eleve: "Eleve") -> None:
        if eleve not in self.eleves:
            self.eleves.append(eleve)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id!r}, nom={self.nom_niveau!r})"
        )

class ListeEtablissement:
    """
    Liste en mémoire utilisée pour la recherche d'établissements
    selon la logique décrite dans l'UML.
    """

    def __init__(self, etablissements: list[Etablissement] | None = None) -> None:
        self.etablissements = etablissements or []

    @staticmethod
    def normaliser_texte(valeur: str) -> str:
        valeur = valeur.strip()
        valeur = " ".join(valeur.split())
        valeur = unicodedata.normalize("NFKD", valeur)
        valeur = valeur.encode("ascii", "ignore").decode("ascii")
        return valeur.upper()

    @classmethod
    def chargerCSV(cls, chemin_fichier: str) -> "ListeEtablissement":
        etablissements = Etablissement.charger_depuis_csv(chemin_fichier)
        return cls(etablissements)

    def rechercher(
        self,
        nom: str,
        nom_academie: str | None = None,
        code_postal: str | None = None,
    ) -> list[Etablissement]:
        nom_normalise = self.normaliser_texte(nom)
        academie_normalisee = (
            self.normaliser_texte(nom_academie) if nom_academie else None
        )
        cp_normalise = code_postal.strip() if code_postal else None

        resultats: list[Etablissement] = []

        for etab in self.etablissements:
            candidat_nom = self.normaliser_texte(etab.getNom())
            if nom_normalise not in candidat_nom:
                continue

            if academie_normalisee:
                candidat_academie = self.normaliser_texte(etab.getNomAcademie() or "")
                if academie_normalisee not in candidat_academie:
                    continue

            if cp_normalise and etab.getCodePostal() != cp_normalise:
                continue

            resultats.append(etab)

        return resultats
