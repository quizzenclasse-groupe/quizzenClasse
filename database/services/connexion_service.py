# database/services/connexion_service.py
# *******************************************************
# Nom ......... : connexion_service.py
# Rôle ........ : Implémente les opérations d'authentification,
#                 de déconnexion et d'inscription des
#                 enseignants, tout en conservant l'utilisateur
#                 actuellement connecté.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/services/connexion_service.py
# Usage ....... : Importer et instancier le service avec une
#                 session SQLAlchemy :
#                 ConnexionService(session)
# *******************************************************
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.models_utilisateurs import Enseignant, Utilisateur
from database.services.iconnexion import IConnexion


class ConnexionService(IConnexion):

    def __init__(self, session: Session) -> None:
        self._session = session
        self._utilisateur_courant: Optional[Utilisateur] = None

    @property
    def utilisateurCourant(self) -> Optional[Utilisateur]:
        return self._utilisateur_courant

    def connecter(
        self,
        nom_utilisateur: str,
        mdp: str
    ) -> Optional[Utilisateur]:

        # Une nouvelle tentative de connexion réinitialise l'état courant.
        self._utilisateur_courant = None

        requete = select(Utilisateur).where(
            Utilisateur.nom_utilisateur == nom_utilisateur
        )

        utilisateur = self._session.execute(
            requete
        ).scalar_one_or_none()

        if utilisateur is None:
            return None

        if not utilisateur.actif:
            return None

        if not utilisateur.verifierMotDePasse(mdp):
            return None

        self._utilisateur_courant = utilisateur
        return utilisateur

    def deconnecter(self) -> None:
        self._utilisateur_courant = None

    def inscrireEnseignant(
        self,
        nom_utilisateur: str,
        mdp: str
    ) -> Enseignant:

        requete = select(Utilisateur).where(
            Utilisateur.nom_utilisateur == nom_utilisateur
        )

        utilisateur_existant = self._session.execute(
            requete
        ).scalar_one_or_none()

        if utilisateur_existant is not None:
            raise ValueError(
                "Ce nom d'utilisateur est déjà utilisé."
            )

        enseignant = Enseignant(
            nom_utilisateur=nom_utilisateur,
            actif=True
        )

        enseignant.definirMotDePasse(mdp)

        try:
            self._session.add(enseignant)
            self._session.commit()
            self._session.refresh(enseignant)

        except Exception:
            self._session.rollback()
            raise

        return enseignant