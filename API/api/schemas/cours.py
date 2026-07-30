# api/schemas/cours.py
# Rôle : Schémas Pydantic pour l'entité Cours (database/models/models_evaluation.py).
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin


from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CoursCreation(BaseModel):
    nom_cours: str = Field(min_length=1, max_length=120)
    description: str | None = None


class CoursMiseAJour(BaseModel):
    nom_cours: str | None = None
    description: str | None = None


class CoursPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_cours: str
    description: str | None = None
    enseignant_id: int
