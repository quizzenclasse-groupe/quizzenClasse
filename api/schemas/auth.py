# api/schemas/auth.py
"""
Schémas Pydantic liés à l'authentification et aux comptes Enseignant.

Rappel du rôle des schémas Pydantic dans une API FastAPI :
  - ils décrivent la forme des données ENTRANTES (validation automatique
    du corps de requête JSON) ;
  - ils décrivent la forme des données SORTANTES (sérialisation propre
    des objets SQLAlchemy en JSON, sans jamais exposer par mégarde un
    champ sensible comme `mdp_hash`).

C'est la principale adaptation nécessaire par rapport au modèle ORM :
les classes `Utilisateur` / `Enseignant` de
`database/models/models_utilisateurs.py` ne sont PAS transmises telles
quelles au client, on les "traduit" via ces schémas.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EnseignantInscription(BaseModel):
    """Corps de requête pour POST /api/auth/register (création de compte)."""

    nom_utilisateur: str = Field(
        min_length=3,
        max_length=30,
        description="Identifiant de connexion, unique dans toute l'application.",
    )
    mot_de_passe: str = Field(
        min_length=8,
        description="Doit contenir au moins 8 caractères (contrôle redondant "
        "avec `Utilisateur.definirMotDePasse`, vérifié aussi côté modèle).",
    )
    nom: str | None = None
    prenom: str | None = None
    email: str | None = None
    date_naissance: date | None = None
    nom_etablissement: str | None = None


class EnseignantConnexion(BaseModel):
    """Corps de requête pour POST /api/auth/login (JSON, alternative au formulaire OAuth2)."""

    nom_utilisateur: str
    mot_de_passe: str


class TokenReponse(BaseModel):
    """Réponse renvoyée après une authentification réussie."""

    access_token: str
    token_type: str = "bearer"


class EnseignantPublic(BaseModel):
    """
    Représentation publique (sans mot de passe) d'un enseignant, renvoyée
    par l'API (ex. GET /api/auth/moi, ou en tant qu'`auteur` imbriqué
    dans un questionnaire).
    """

    # `from_attributes=True` (anciennement `orm_mode`) permet de construire
    # ce schéma directement à partir d'un objet SQLAlchemy `Enseignant`,
    # via `EnseignantPublic.model_validate(objet_orm)`.
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_utilisateur: str
    nom: str | None = None
    prenom: str | None = None
    email: str | None = None
    nom_etablissement: str | None = None
    actif: bool
