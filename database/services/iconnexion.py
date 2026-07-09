# database/services/iconnexion.py

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