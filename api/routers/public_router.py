# api/routers/public_router.py
"""
Routes PUBLIQUES (aucune authentification requise) permettant à un
élève de répondre à un questionnaire depuis son propre appareil, à
partir du lien/code partagé par l'enseignant.

Séparées dans leur propre routeur (préfixe /api/public) plutôt que
mélangées avec /api/sessions : cela rend explicite, rien qu'à la
lecture de la liste des routes, quelles requêtes ne nécessitent PAS de
jeton JWT — un point sensible qu'il ne faut pas laisser implicite.
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
