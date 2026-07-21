# api/security.py
# Rôle : Couche sécurité de l'API : émission/validation des JWT et dépendances.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin


from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.config import settings
from api.deps import get_db
from database.models.models_utilisateurs import Enseignant, Utilisateur

# Déclare à FastAPI où se trouve l'endpoint de login (utilisé uniquement
# pour générer la documentation Swagger : le bouton "Authorize").
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def creer_access_token(utilisateur: Utilisateur) -> str:
    """
    Construit un JWT signé pour l'utilisateur donné.

    Le token contient :
      - "sub" : l'identifiant de l'utilisateur (obligatoire pour un JWT) ;
      - "role" : le type polymorphique ("enseignant" ou "admin"), pratique
        côté frontend pour adapter l'affichage sans requête supplémentaire ;
      - "exp" : la date d'expiration du token.
    """
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(utilisateur.id),
        "role": utilisateur.type_utilisateur,
        "exp": expiration,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decoder_token(token: str) -> dict:
    """
    Décode et vérifie la signature/expiration d'un token.
    Lève une HTTPException 401 si le token est invalide ou expiré.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le jeton d'authentification a expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: OrmSession = Depends(get_db),
) -> Utilisateur:
    """
    Dépendance FastAPI à injecter dans les endpoints protégés :

        @router.get("/moi")
        def moi(utilisateur: Utilisateur = Depends(get_current_user)):
            ...

    Décode le token, récupère l'utilisateur en base et vérifie qu'il est
    toujours actif (un compte désactivé ne doit plus pouvoir s'authentifier
    même avec un token encore valide).
    """
    payload = _decoder_token(token)

    id_utilisateur: Optional[str] = payload.get("sub")

    if id_utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide (sujet manquant).",
        )

    utilisateur = db.execute(
        select(Utilisateur).where(Utilisateur.id == int(id_utilisateur))
    ).scalar_one_or_none()

    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable.",
        )

    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a été désactivé.",
        )

    return utilisateur


def get_current_enseignant(
    utilisateur: Utilisateur = Depends(get_current_user),
) -> Enseignant:

    if utilisateur.type_utilisateur not in ("enseignant", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette action est réservée aux enseignants.",
        )

    return utilisateur  # type: ignore[return-value]


def est_admin(utilisateur: Utilisateur) -> bool:
    """Petit utilitaire réutilisé par la couche service pour les contrôles de droits."""
    return utilisateur.type_utilisateur == "admin"


# Code d'accès élève à une session

# Pour permettre à un élève de répondre à un questionnaire depuis son
# propre appareil sans devoir créer de compte élève (absent du modèle de données
# d'origine, voir Participant/Eleve), on génère un code court dérivé de
# manière déterministe de l'identifiant de session et de la clé secrète
# de l'application (HMAC-SHA256, tronqué à 6 caractères hexadécimaux).
#
# Avantage de cette approche : aucune colonne supplémentaire
# à ajouter au modèle Niveau/SessionQuestionnaire (donc aucune migration
# de base de données nécessaire), le code se recalcule à la demande et
# se vérifie de la même façon.


def code_acces_session(session_id: int) -> str:
    """Calcule le code d'accès public (6 caractères) d'une session."""
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        f"session-publique-{session_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return signature[:6]


def verifier_code_session(session_id: int, code_fourni: str) -> bool:
    """
    Compare le code fourni au code attendu, en temps constant
    (`hmac.compare_digest`) pour éviter les attaques par mesure de temps.
    """
    return hmac.compare_digest(code_acces_session(session_id), (code_fourni or "").lower())
