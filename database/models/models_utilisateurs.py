# database/models/models_utilisateurs.py
# *******************************************************
# Nom ......... : models_utilisateurs.py
# Rôle ........ : Définit les modèles ORM représentant les
#                 utilisateurs, les enseignants et les
#                 administrateurs ; assure le hachage et la
#                 vérification sécurisée des mots de passe.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/models/models_utilisateurs.py
# Usage ....... : Importer les modèles nécessaires, par exemple :
#                 from database.models.models_utilisateurs \
#                 import Utilisateur, Enseignant, Admin
# *******************************************************
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from sqlalchemy import Boolean, String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date
from typing import TYPE_CHECKING

from database.base import Model



class Utilisateur(Model):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nom_utilisateur: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    mdp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    type_utilisateur: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __mapper_args__ = {
        "polymorphic_on": type_utilisateur,
        "polymorphic_identity": "utilisateur",
    }

    def definirMotDePasse(self, mot_de_passe: str) -> None:
        if len(mot_de_passe) < 8:
            raise ValueError(
                "Le mot de passe doit contenir au moins huit caractères."
            )

        iterations = 260_000
        salt = secrets.token_bytes(16)

        empreinte = hashlib.pbkdf2_hmac(
            "sha256",
            mot_de_passe.encode("utf-8"),
            salt,
            iterations,
        )

        self.mdp_hash = "$".join(
            [
                "pbkdf2_sha256",
                str(iterations),
                base64.b64encode(salt).decode("ascii"),
                base64.b64encode(empreinte).decode("ascii"),
            ]
        )

    def verifierMotDePasse(self, mot_de_passe: str) -> bool:
        try:
            algorithme, iterations, salt_b64, empreinte_b64 = (
                self.mdp_hash.split("$", maxsplit=3)
            )

            if algorithme != "pbkdf2_sha256":
                return False

            salt = base64.b64decode(salt_b64)
            empreinte_attendue = base64.b64decode(empreinte_b64)

            empreinte_calculee = hashlib.pbkdf2_hmac(
                "sha256",
                mot_de_passe.encode("utf-8"),
                salt,
                int(iterations),
            )

        except (ValueError, TypeError):
            return False

        return hmac.compare_digest(
            empreinte_calculee,
            empreinte_attendue,
        )

    def getId(self) -> int:
        return self.id

    def getNomUtilisateur(self) -> str:
        return self.nom_utilisateur

    def getActif(self) -> bool:
        return self.actif

    def setActif(self, actif: bool) -> None:
        self.actif = actif


class Enseignant(Utilisateur):
    nom: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    prenom: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(200),
        unique=True,
        nullable=True,
    )

    date_naissance: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    nom_etablissement: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    cours_enseignes: Mapped[list["Cours"]] = relationship(
        back_populates="enseignant",
    )

    rapports_auteurs: Mapped[list["Rapport"]] = relationship(
        back_populates="enseignant",
    )

    __mapper_args__ = {
        "polymorphic_identity": "enseignant",
    }

class Admin(Utilisateur):
    """
    Utilisateur disposant des droits d'administration.

    La classe utilise l'héritage sur table unique : ses données sont
    enregistrées dans la table « utilisateurs » héritée de Utilisateur.
    """

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id!r}, nom={self.nom_utilisateur!r}, actif={self.actif!r})"
        )