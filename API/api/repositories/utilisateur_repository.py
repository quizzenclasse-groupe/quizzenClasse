# api/repositories/utilisateur_repository.py
# Rôle : Accès à la base de données  pour les comptes Utilisateur et Enseignant.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.repositories.base import BaseRepository
from database.models.models_utilisateurs import Enseignant, Utilisateur


class UtilisateurRepository(BaseRepository[Utilisateur]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Utilisateur)

    def par_nom_utilisateur(self, nom_utilisateur: str) -> Utilisateur | None:
        return self.session.execute(
            select(Utilisateur).where(
                Utilisateur.nom_utilisateur == nom_utilisateur
            )
        ).scalar_one_or_none()

    def creer_enseignant(self, enseignant: Enseignant) -> Enseignant:
        self.session.add(enseignant)
        self.session.commit()
        self.session.refresh(enseignant)
        return enseignant
