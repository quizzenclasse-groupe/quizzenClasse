# api/services/auth_service.py
# Rôle : Service d'authentification
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

"""
(logique métier déjà existante dans database/services/connexion_service.py, utilisée telle quelle par le
programme console) et la génération de JWT (couche ajoutée pour l'API).
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from api.schemas.auth import EnseignantInscription, TokenReponse
from api.security import creer_access_token
from database.models.models_utilisateurs import Enseignant
from database.services.connexion_service import ConnexionService


class AuthService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        # Réutilisation directe du service métier existant : c'est lui qui
        # sait comment vérifier un mot de passe et créer un enseignant.
        self._connexion = ConnexionService(session)

    def inscrire(self, donnees: EnseignantInscription) -> Enseignant:
        """
        Crée un compte Enseignant.

        `ConnexionService.inscrireEnseignant` ne gère que
        `nom_utilisateur` / mot de passe ; les champs de profil
        complémentaires (nom, prénom, email...) propres au modèle
        `Enseignant` de QuizzenClasse (absents du modèle Quiz_app
        d'origine) sont appliqués juste après, avant le commit final.
        """
        try:
            enseignant = self._connexion.inscrireEnseignant(
                nom_utilisateur=donnees.nom_utilisateur,
                mdp=donnees.mot_de_passe,
            )
        except ValueError as exc:
            # Nom d'utilisateur déjà pris, ou mot de passe trop court
            # (levé par `Utilisateur.definirMotDePasse`).
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

        champs_profil = donnees.model_dump(
            exclude={"nom_utilisateur", "mot_de_passe"}, exclude_none=True
        )
        for champ, valeur in champs_profil.items():
            setattr(enseignant, champ, valeur)

        self.session.commit()
        self.session.refresh(enseignant)

        return enseignant

    def connecter(self, nom_utilisateur: str, mot_de_passe: str) -> TokenReponse:
        """Vérifie les identifiants puis émet un token JWT."""
        utilisateur = self._connexion.connecter(nom_utilisateur, mot_de_passe)

        if utilisateur is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = creer_access_token(utilisateur)
        return TokenReponse(access_token=token)
