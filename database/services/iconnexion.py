# database/services/iconnexion.py
# *******************************************************
# Nom ......... : iconnexion.py
# Rôle ........ : Définit l'interface abstraite du service de
#                 connexion en imposant les opérations
#                 d'authentification, de déconnexion et
#                 d'inscription des enseignants.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/services/iconnexion.py
# Usage ....... : Hériter de l'interface afin d'implémenter
#                 un service de connexion :
#                 class ConnexionService(IConnexion)
# *******************************************************
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from database.models.models_utilisateurs import Enseignant, Utilisateur


class IConnexion(ABC):

    @abstractmethod
    def connecter(
        self,
        nom_utilisateur: str,
        mdp: str
    ) -> Optional[Utilisateur]:
        """Authentifie un utilisateur et le renvoie si la connexion réussit."""
        pass

    @abstractmethod
    def deconnecter(self) -> None:
        """Déconnecte l'utilisateur courant."""
        pass

    @abstractmethod
    def inscrireEnseignant(
        self,
        nom_utilisateur: str,
        mdp: str
    ) -> Enseignant:
        """Crée et renvoie un nouvel enseignant."""
        pass