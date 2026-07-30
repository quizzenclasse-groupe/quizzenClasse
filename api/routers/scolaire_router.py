# api/routers/scolaire_router.py
"""Routes HTTP pour établissements, niveaux, élèves et équipes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.scolaire import (
    EleveCreation,
    EleveMiseAJour,
    ElevePublic,
    EquipeCreation,
    EquipePublic,
    EtablissementPublic,
    NiveauCreation,
    NiveauMiseAJour,
    NiveauPublic,
)
from api.security import get_current_enseignant
from api.services.scolaire_service import (
    EleveService,
    EquipeService,
    EtablissementService,
    NiveauService,
)
from database.models.models_utilisateurs import Enseignant

router = APIRouter(prefix="/api", tags=["Parcours scolaire"])


# ----------------------------------------------------------------------------
# Établissements (lecture seule : l'import CSV massif reste une opération
# console, cf. `python main.py seed-etabs` dans le README)
# ----------------------------------------------------------------------------


@router.get(
    "/etablissements",
    response_model=list[EtablissementPublic],
    summary="Rechercher un établissement par nom",
)
def rechercher_etablissements(
    q: str = Query(min_length=1, description="Terme recherché dans le nom de l'établissement."),
    db: OrmSession = Depends(get_db),
    _enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[EtablissementPublic]:
    resultats = EtablissementService(db).rechercher(q)
    return [EtablissementPublic.model_validate(e) for e in resultats]


# ----------------------------------------------------------------------------
# Niveaux
# ----------------------------------------------------------------------------


@router.get("/niveaux", response_model=list[NiveauPublic], summary="Lister mes niveaux")
def lister_niveaux(
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[NiveauPublic]:
    niveaux = NiveauService(db).lister_pour(enseignant)
    return [NiveauPublic.depuis_orm(n) for n in niveaux]


@router.post(
    "/niveaux", response_model=NiveauPublic, status_code=201, summary="Créer un niveau"
)
def creer_niveau(
    donnees: NiveauCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> NiveauPublic:
    niveau = NiveauService(db).creer(donnees, enseignant)
    return NiveauPublic.depuis_orm(niveau)


@router.patch(
    "/niveaux/{niveau_id}", response_model=NiveauPublic, summary="Renommer un niveau"
)
def renommer_niveau(
    niveau_id: int,
    donnees: NiveauMiseAJour,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> NiveauPublic:
    niveau = NiveauService(db).renommer(niveau_id, donnees, enseignant)
    return NiveauPublic.depuis_orm(niveau)


@router.delete("/niveaux/{niveau_id}", status_code=204, response_model=None, summary="Supprimer un niveau")
def supprimer_niveau(
    niveau_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> None:
    NiveauService(db).supprimer(niveau_id, enseignant)


# ----------------------------------------------------------------------------
# Élèves
# ----------------------------------------------------------------------------


@router.get(
    "/niveaux/{niveau_id}/eleves",
    response_model=list[ElevePublic],
    summary="Lister les élèves d'un niveau",
)
def lister_eleves_du_niveau(
    niveau_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[ElevePublic]:
    eleves = EleveService(db).lister_par_niveau(niveau_id, enseignant)
    return [ElevePublic.depuis_orm(e) for e in eleves]


@router.post(
    "/eleves", response_model=ElevePublic, status_code=201, summary="Ajouter un élève"
)
def creer_eleve(
    donnees: EleveCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> ElevePublic:
    eleve = EleveService(db).creer(donnees, enseignant)
    return ElevePublic.depuis_orm(eleve)


@router.get("/eleves/{eleve_id}", response_model=ElevePublic, summary="Détail d'un élève")
def obtenir_eleve(
    eleve_id: int,
    db: OrmSession = Depends(get_db),
    _enseignant: Enseignant = Depends(get_current_enseignant),
) -> ElevePublic:
    eleve = EleveService(db).obtenir(eleve_id)
    return ElevePublic.depuis_orm(eleve)


@router.patch(
    "/eleves/{eleve_id}", response_model=ElevePublic, summary="Modifier un élève"
)
def modifier_eleve(
    eleve_id: int,
    donnees: EleveMiseAJour,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> ElevePublic:
    eleve = EleveService(db).modifier(eleve_id, donnees, enseignant)
    return ElevePublic.depuis_orm(eleve)


# ----------------------------------------------------------------------------
# Équipes
# ----------------------------------------------------------------------------


@router.post(
    "/equipes", response_model=EquipePublic, status_code=201, summary="Créer une équipe"
)
def creer_equipe(
    donnees: EquipeCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> EquipePublic:
    equipe = EquipeService(db).creer(donnees, enseignant)
    return EquipePublic.model_validate(equipe)


@router.get("/equipes/{equipe_id}", response_model=EquipePublic, summary="Détail d'une équipe")
def obtenir_equipe(
    equipe_id: int,
    db: OrmSession = Depends(get_db),
    _enseignant: Enseignant = Depends(get_current_enseignant),
) -> EquipePublic:
    equipe = EquipeService(db).obtenir(equipe_id)
    return EquipePublic.model_validate(equipe)
