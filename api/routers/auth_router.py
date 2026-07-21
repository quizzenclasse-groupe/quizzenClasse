# api/routers/auth_router.py
# Rôle :Routes HTTP d'authentification : inscription, connexion, profil courant.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.auth import (
    EnseignantConnexion,
    EnseignantInscription,
    EnseignantPublic,
    TokenReponse,
)
from api.security import get_current_user
from api.services.auth_service import AuthService
from database.models.models_utilisateurs import Utilisateur

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post(
    "/register",
    response_model=EnseignantPublic,
    status_code=201,
    summary="Créer un compte enseignant",
)
def inscription(
    donnees: EnseignantInscription, db: OrmSession = Depends(get_db)
) -> EnseignantPublic:
    enseignant = AuthService(db).inscrire(donnees)
    return EnseignantPublic.model_validate(enseignant)


@router.post(
    "/login",
    response_model=TokenReponse,
    summary="Se connecter (formulaire OAuth2, pour Swagger et le frontend)",
)
def connexion_formulaire(
    identifiants: OAuth2PasswordRequestForm = Depends(),
    db: OrmSession = Depends(get_db),
) -> TokenReponse:
    """
    Utilise le format standard `OAuth2PasswordRequestForm`
    (`application/x-www-form-urlencoded`, champs `username`/`password`)
    attendu par le bouton "Authorize" de Swagger UI et par la plupart
    des bibliothèques HTTP clientes.
    """
    return AuthService(db).connecter(
        nom_utilisateur=identifiants.username,
        mot_de_passe=identifiants.password,
    )


@router.post(
    "/login-json",
    response_model=TokenReponse,
    summary="Se connecter (corps JSON, alternative pratique pour le frontend React)",
)
def connexion_json(
    identifiants: EnseignantConnexion, db: OrmSession = Depends(get_db)
) -> TokenReponse:
    return AuthService(db).connecter(
        nom_utilisateur=identifiants.nom_utilisateur,
        mot_de_passe=identifiants.mot_de_passe,
    )


@router.get(
    "/moi",
    response_model=EnseignantPublic,
    summary="Profil de l'utilisateur actuellement authentifié",
)
def profil_courant(
    utilisateur: Utilisateur = Depends(get_current_user),
) -> EnseignantPublic:
    return EnseignantPublic.model_validate(utilisateur)
