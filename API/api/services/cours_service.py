# api/services/cours_service.py
# Rôle : Service métier pour l'entité Cours
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin


from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from api.repositories.cours_repository import CoursRepository
from api.schemas.cours import CoursCreation, CoursMiseAJour
from api.security import est_admin
from database.models.models_evaluation import Cours
from database.models.models_utilisateurs import Utilisateur


class CoursService:
    def __init__(self, session: OrmSession) -> None:
        self.repo = CoursRepository(session)

    def lister_pour(self, enseignant: Utilisateur) -> list[Cours]:
        if est_admin(enseignant):
            return self.repo.lister()
        return self.repo.par_enseignant(enseignant.id)

    def obtenir(self, cours_id: int) -> Cours:
        cours = self.repo.obtenir(cours_id)
        if cours is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable."
            )
        return cours

    def _verifier_proprietaire(self, cours: Cours, enseignant: Utilisateur) -> None:
        if est_admin(enseignant):
            return
        if cours.enseignant_id != enseignant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez agir que sur vos propres cours.",
            )

    def creer(self, donnees: CoursCreation, enseignant: Utilisateur) -> Cours:
        cours = Cours(
            nom_cours=donnees.nom_cours.strip(),
            description=donnees.description,
            enseignant_id=enseignant.id,
        )
        return self.repo.ajouter(cours)

    def modifier(
        self, cours_id: int, donnees: CoursMiseAJour, enseignant: Utilisateur
    ) -> Cours:
        cours = self.obtenir(cours_id)
        self._verifier_proprietaire(cours, enseignant)

        if donnees.nom_cours is not None:
            cours.nom_cours = donnees.nom_cours.strip()
        if donnees.description is not None:
            cours.description = donnees.description

        return self.repo.sauvegarder(cours)

    def supprimer(self, cours_id: int, enseignant: Utilisateur) -> None:
        cours = self.obtenir(cours_id)
        self._verifier_proprietaire(cours, enseignant)
        self.repo.supprimer(cours)
