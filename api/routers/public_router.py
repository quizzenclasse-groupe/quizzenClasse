# api/routers/public_router.py
# Rôle : Routes publiques qui permet aux élèves de répondre aux questionnaires via un lien partagé par leur enseignant.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

"""
Routes publiques (car aucune authentification requise) qui permettent à un
élève de répondre à un questionnaire depuis sa propre machine, à
partir du lien/code que l'enseignant aura partagé.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.session import ResultatSoumission, SessionPubliquePourEleve, SoumissionReponses
from api.services.session_service import ParticipationPubliqueService

router = APIRouter(prefix="/api/public", tags=["Accès élève (public)"])


@router.get(
    "/sessions/{session_id}/{code}",
    response_model=SessionPubliquePourEleve,
    summary="Ouvrir une session avec le code d'accès (vue élève, sans les bonnes réponses)",
)
def ouvrir_session_publique(
    session_id: int,
    code: str,
    db: OrmSession = Depends(get_db),
) -> SessionPubliquePourEleve:
    return ParticipationPubliqueService(db).obtenir_pour_eleve(session_id, code)


@router.post(
    "/sessions/{session_id}/{code}/reponses",
    response_model=ResultatSoumission,
    summary="Soumettre les réponses d'un élève (correction automatique)",
)
def soumettre_reponses_publiques(
    session_id: int,
    code: str,
    donnees: SoumissionReponses,
    db: OrmSession = Depends(get_db),
) -> ResultatSoumission:
    return ParticipationPubliqueService(db).soumettre(session_id, code, donnees)
