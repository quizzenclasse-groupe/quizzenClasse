# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Stockage local de démonstration conservé pour les essais hors connexion.

"""
Service de stockage temporaire de QuizzenClasse.

Version : GUI V1.1

Ce fichier contient la classe DataStore, chargée de conserver temporairement
les niveaux et les élèves pendant l'exécution de l'application.

Dans une future version, ce stockage local pourra être remplacé par des appels
à l'API sans modifier profondément les fenêtres graphiques.

Remarque de relecture : DataStore est instanciée dans gui_main.py
(self.data_store) mais n'est en fait appelée par aucune fenêtre de la GUI
actuelle, tout passe par api_client (ApiClient ou LocalClient). C'est un
reliquat d'une version antérieure où les niveaux/élèves étaient gérés en
mémoire avant le passage à l'API ; gardé ici car il pourrait resservir en
mode hors ligne, mais il n'est pas branché sur le LocalClient actuel.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Optional


class DataStore:
    """Stockage en mémoire des niveaux et des élèves (non relié à la GUI active, voir docstring du module)."""

    def __init__(self) -> None:
        self._niveaux: list[dict] = []
        self._eleves: list[dict] = []

        # Ces compteurs produisent des identifiants temporaires uniques.
        self._next_niveau_id = 1
        self._next_eleve_id = 1

    # ------------------------------------------------------------------
    # Gestion des niveaux
    # ------------------------------------------------------------------

    def get_niveaux(self) -> list[dict]:
        return deepcopy(self._niveaux)

    def get_niveau_by_id(self, niveau_id: int) -> Optional[dict]:
        for niveau in self._niveaux:
            if niveau["id"] == niveau_id:
                return deepcopy(niveau)
        return None

    def add_niveau(
        self,
        nom_niveau: str,
        matiere: str,
        ville: str,
        etablissement: str,
    ) -> dict:
        niveau = {
            "id": self._next_niveau_id,
            "nom_niveau": nom_niveau,
            "matiere": matiere,
            "ville": ville,
            "etablissement": etablissement,
        }

        self._niveaux.append(niveau)
        self._next_niveau_id += 1

        return deepcopy(niveau)

    def update_niveau(
        self,
        niveau_id: int,
        nom_niveau: str,
        matiere: str,
        ville: str,
        etablissement: str,
    ) -> bool:
        for niveau in self._niveaux:
            if niveau["id"] == niveau_id:
                niveau["nom_niveau"] = nom_niveau
                niveau["matiere"] = matiere
                niveau["ville"] = ville
                niveau["etablissement"] = etablissement
                return True

        return False

    def delete_niveau(self, niveau_id: int) -> bool:
        # On refuse de supprimer un niveau qui a encore des élèves rattachés.
        if self.niveau_has_eleves(niveau_id):
            return False

        for index, niveau in enumerate(self._niveaux):
            if niveau["id"] == niveau_id:
                del self._niveaux[index]
                return True

        return False

    def niveau_has_eleves(self, niveau_id: int) -> bool:
        return any(
            eleve["niveau_id"] == niveau_id
            for eleve in self._eleves
        )

    def niveau_name_exists(
        self,
        nom_niveau: str,
        etablissement: str,
        ignored_niveau_id: Optional[int] = None,) -> bool:
        """Vérifie si un niveau du même nom existe déjà dans le même établissement (pour éviter les doublons)."""
        normalized_name = nom_niveau.strip().casefold()
        normalized_etablissement = etablissement.strip().casefold()

        for niveau in self._niveaux:
            if ignored_niveau_id == niveau["id"]:
                continue

            existing_name = niveau["nom_niveau"].strip().casefold()
            existing_etablissement = (
                niveau["etablissement"].strip().casefold()
            )   

            if (
               existing_name == normalized_name
               and existing_etablissement == normalized_etablissement
            ):
               return True

        return False

    # ------------------------------------------------------------------
    # Gestion des élèves
    # ------------------------------------------------------------------

    def get_eleves(self) -> list[dict]:
        return deepcopy(self._eleves)

    def get_eleve_by_id(self, eleve_id: int) -> Optional[dict]:
        for eleve in self._eleves:
            if eleve["id"] == eleve_id:
                return deepcopy(eleve)
        return None

    def add_eleve(
        self,
        nom_eleve: str,
        prenom: str,
        date_naissance: str,
        redoublant: bool,
        ville: str,
        cp: str,
        niveau_id: int,
    ) -> dict:
        eleve = {
            "id": self._next_eleve_id,
            "nom_eleve": nom_eleve,
            "prenom": prenom,
            "date_naissance": date_naissance,
            "redoublant": redoublant,
            "ville": ville,
            "cp": cp,
            "niveau_id": niveau_id,
        }

        self._eleves.append(eleve)
        self._next_eleve_id += 1

        return deepcopy(eleve)

    def update_eleve(
        self,
        eleve_id: int,
        nom_eleve: str,
        prenom: str,
        date_naissance: str,
        redoublant: bool,
        ville: str,
        cp: str,
        niveau_id: int,
    ) -> bool:
        for eleve in self._eleves:
            if eleve["id"] == eleve_id:
                eleve["nom_eleve"] = nom_eleve
                eleve["prenom"] = prenom
                eleve["date_naissance"] = date_naissance
                eleve["redoublant"] = redoublant
                eleve["ville"] = ville
                eleve["cp"] = cp
                eleve["niveau_id"] = niveau_id
                return True

        return False

    def delete_eleve(self, eleve_id: int) -> bool:
        # Contrairement à l'API réelle (voir le rapport), cette version de
        # démo autorise bien la suppression d'un élève.
        for index, eleve in enumerate(self._eleves):
            if eleve["id"] == eleve_id:
                del self._eleves[index]
                return True

        return False

    def get_eleves_by_niveau(self, niveau_id: int) -> list[dict]:
        return [
            deepcopy(eleve)
            for eleve in self._eleves
            if eleve["niveau_id"] == niveau_id
        ]
