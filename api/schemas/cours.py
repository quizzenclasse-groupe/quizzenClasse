# api/schemas/cours.py
"""Schémas Pydantic pour l'entité Cours (database/models/models_evaluation.py)."""

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
