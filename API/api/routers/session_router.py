# api/routers/session_router.py
# Rôle : Routes HTTP pour les sessions de questionnaire, participations et rapports.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.session import (
    ParticipationCreation,
    ParticipationEvaluation,
    ParticipationPublic,
    RapportSessionPublic,
    SessionCreation,
    SessionPublic,
    StatistiquesSessionPublic,
)
from api.security import get_current_enseignant
from api.services.session_service import ParticipationService, RapportService, SessionService
from database.models.models_utilisateurs import Enseignant

router = APIRouter(prefix="/api", tags=["Sessions & évaluation"])


# Sessions

@router.get(
    "/sessions/{session_id}",
    response_model=SessionPublic,
    summary="Détail d'une session (statut courant)",
)
def obtenir_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> SessionPublic:
    session_q = SessionService(db).obtenir_pour(session_id, enseignant)
    return SessionPublic.model_validate(session_q)


@router.get(
    "/questionnaires/{questionnaire_id}/sessions",
    response_model=list[SessionPublic],
    summary="Lister les sessions d'un questionnaire",
)
def lister_sessions(
    questionnaire_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[SessionPublic]:
    sessions = SessionService(db).lister_par_questionnaire(questionnaire_id, enseignant)
    return [SessionPublic.model_validate(s) for s in sessions]


@router.post(
    "/sessions", response_model=SessionPublic, status_code=201, summary="Créer une session"
)
def creer_session(
    donnees: SessionCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> SessionPublic:
    session_q = SessionService(db).creer(donnees, enseignant)
    return SessionPublic.model_validate(session_q)


@router.post(
    "/sessions/{session_id}/demarrer",
    response_model=SessionPublic,
    summary="Démarrer une session (fixe la date de début)",
)
def demarrer_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> SessionPublic:
    return SessionPublic.model_validate(SessionService(db).demarrer(session_id, enseignant))


@router.post(
    "/sessions/{session_id}/cloturer",
    response_model=SessionPublic,
    summary="Clôturer une session (fixe la date de fin)",
)
def cloturer_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> SessionPublic:
    return SessionPublic.model_validate(SessionService(db).cloturer(session_id, enseignant))


@router.get(
    "/sessions/{session_id}/code-partage",
    summary="Récupérer le code à transmettre aux élèves pour répondre en ligne",
)
def code_partage_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> dict[str, str]:
    code = SessionService(db).obtenir_code_partage(session_id, enseignant)
    return {"code": code}


# Participations

@router.get(
    "/sessions/{session_id}/participations",
    response_model=list[ParticipationPublic],
    summary="Lister les participations d'une session",
)
def lister_participations(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[ParticipationPublic]:
    participations = ParticipationService(db).lister_par_session(session_id, enseignant)
    return [ParticipationPublic.model_validate(p) for p in participations]


@router.post(
    "/sessions/{session_id}/participations",
    response_model=ParticipationPublic,
    status_code=201,
    summary="Inscrire un participant (élève ou équipe) à une session",
)
def inscrire_participation(
    session_id: int,
    donnees: ParticipationCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> ParticipationPublic:
    participation = ParticipationService(db).inscrire(session_id, donnees, enseignant)
    return ParticipationPublic.model_validate(participation)


@router.patch(
    "/participations/{participation_id}/evaluer",
    response_model=ParticipationPublic,
    summary="Noter une participation",
)
def evaluer_participation(
    participation_id: int,
    donnees: ParticipationEvaluation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> ParticipationPublic:
    participation = ParticipationService(db).evaluer(participation_id, donnees, enseignant)
    return ParticipationPublic.model_validate(participation)



# Statistiques / rapport


@router.get(
    "/sessions/{session_id}/statistiques",
    response_model=StatistiquesSessionPublic,
    summary="Statistiques calculées d'une session (moyenne, taux de réussite...)",
)
def statistiques_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> StatistiquesSessionPublic:
    stats = RapportService(db).statistiques(session_id, enseignant)
    return StatistiquesSessionPublic.model_validate(stats)


@router.get(
    "/sessions/{session_id}/rapport",
    response_model=RapportSessionPublic,
    summary="Rapport complet d'une session (statistiques + date de génération)",
)
def rapport_session(
    session_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> RapportSessionPublic:
    rapport = RapportService(db).rapport(session_id, enseignant)
    return RapportSessionPublic.model_validate(rapport)
