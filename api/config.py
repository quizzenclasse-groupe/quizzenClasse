# api/config.py
"""
Configuration centralisée de l'API QuizzenClasse.

Toutes les valeurs sensibles (clé secrète JWT, durée de vie des tokens...)
sont lues depuis les variables d'environnement (fichier .env à la racine
du projet, déjà chargé par `database.engine` via `python-dotenv`).

On centralise ces réglages ici pour :
  - éviter de disperser des `os.getenv(...)` dans tout le code ;
  - avoir un seul endroit à modifier si on change de stratégie
    d'authentification (durée du token, algorithme, etc.) ;
  - faciliter les tests (on peut monkeypatcher `settings`).
"""

from __future__ import annotations

import os

# NOTE : database.engine importe déjà `load_dotenv(BASE_DIR / ".env")`.
# On importe ce module ici uniquement pour garantir que le .env est chargé
# avant de lire nos propres variables d'environnement, même si api.config
# est importé avant database.engine ailleurs dans le projet.
from database.engine import BASE_DIR  # noqa: F401  (import déclenche le load_dotenv)


class Settings:
    """
    Regroupe les paramètres de configuration de la couche API.

    Ces attributs sont volontairement simples (pas de librairie de
    validation type pydantic-settings) pour rester cohérent avec le reste
    du projet, qui n'utilise pas encore FastAPI/Pydantic ailleurs.
    """

    # Clé secrète utilisée pour signer les JSON Web Tokens (JWT).
    # ATTENTION : en production, cette clé DOIT être définie dans le .env
    # et ne jamais être commitée. Une valeur par défaut est fournie
    # uniquement pour permettre de lancer le projet en développement local.
    SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "cle-de-developpement-a-ne-jamais-utiliser-en-production",
    )

    # Algorithme de signature du token. HS256 = signature symétrique,
    # suffisant ici car un seul service (notre API) émet et vérifie
    # les tokens (pas de scénario multi-services / clé publique).
    ALGORITHM: str = "HS256"

    # Durée de validité d'un token d'accès, en minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    )

    # Origines autorisées pour le CORS (le frontend React tourne sur un
    # port différent du backend en développement : Vite -> 5173,
    # FastAPI/uvicorn -> 8000).
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")


# Instance unique importée partout ailleurs : `from api.config import settings`.
settings = Settings()
