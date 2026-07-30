# api/routers/cours_router.py
"""Routes HTTP pour l'entité Cours."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.cours import CoursCreation, CoursMiseAJour, CoursPublic
from api.security import get_current_enseignant
from api.services.cours_service import CoursService
from database.models.models_utilisateurs import Enseignant

router = APIRouter(prefix="/api/cours", tags=["Cours"])


@router.get("", response_model=list[CoursPublic], summary="Lister mes cours")
def lister_cours(
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[CoursPublic]:
    return [CoursPublic.model_validate(c) for c in CoursService(db).lister_pour(enseignant)]


@router.post("", response_model=CoursPublic, status_code=201, summary="Créer un cours")
def creer_cours(
    donnees: CoursCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> CoursPublic:
    return CoursPublic.model_validate(CoursService(db).creer(donnees, enseignant))


@router.get("/{cours_id}", response_model=CoursPublic, summary="Détail d'un cours")
def obtenir_cours(
    cours_id: int,
    db: OrmSession = Depends(get_db),
    _enseignant: Enseignant = Depends(get_current_enseignant),
) -> CoursPublic:
    return CoursPublic.model_validate(CoursService(db).obtenir(cours_id))


@router.patch("/{cours_id}", response_model=CoursPublic, summary="Modifier un cours")
def modifier_cours(
    cours_id: int,
    donnees: CoursMiseAJour,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> CoursPublic:
    return CoursPublic.model_validate(
        CoursService(db).modifier(cours_id, donnees, enseignant)
    )


@router.delete("/{cours_id}", status_code=204, response_model=None, summary="Supprimer un cours")
def supprimer_cours(
    cours_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> None:
    CoursService(db).supprimer(cours_id, enseignant)
