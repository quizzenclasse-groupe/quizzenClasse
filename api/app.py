# api/app.py
"""
Point d'entrée de l'API QuizzenClasse.

Lancement en développement :

    uvicorn api.app:app --reload --port 8000

Documentation interactive générée automatiquement par FastAPI :
    http://127.0.0.1:8000/docs   (Swagger UI)
    http://127.0.0.1:8000/redoc  (ReDoc)
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database.models  # noqa: F401  (enregistre tous les modèles ORM avant create_all)
from database.base import Model
from database.engine import engine

from api.config import settings
from api.routers import (
    auth_router,
    cours_router,
    public_router,
    questionnaire_router,
    scolaire_router,
    session_router,
)

app = FastAPI(
    title="QuizzenClasse API",
    description=(
        "API REST adaptée du projet Quiz_app pour l'application "
        "QuizzenClasse (gestion de questionnaires pédagogiques, "
        "établissements, niveaux, élèves, équipes, sessions et "
        "statistiques)."
    ),
    version="1.0.0",
)

# Autorise le frontend React (servi sur un autre port en développement)
# à appeler cette API depuis le navigateur.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def creer_les_tables_si_absentes() -> None:
    """
    Reprend exactement le comportement du programme console
    (`main.py`, ligne `Model.metadata.create_all(bind=engine)`) :
    les tables manquantes sont créées automatiquement au démarrage,
    les tables déjà présentes ne sont pas touchées.
    """
    Model.metadata.create_all(bind=engine)


# Chaque router porte déjà son propre préfixe ("/api/...") et ses tags,
# définis dans les fichiers correspondants sous api/routers/.
app.include_router(auth_router.router)
app.include_router(scolaire_router.router)
app.include_router(cours_router.router)
app.include_router(questionnaire_router.router)
app.include_router(session_router.router)
app.include_router(public_router.router)


@app.get("/api/sante", tags=["Divers"], summary="Vérification de disponibilité de l'API")
def sante() -> dict[str, str]:
    return {"statut": "ok"}
