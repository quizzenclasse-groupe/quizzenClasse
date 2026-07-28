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
"""

from __future__ import annotations

from copy import deepcopy
from typing import Optional


class DataStore:
    """
    Représente data store dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self._niveaux: list[dict] = []
        self._eleves: list[dict] = []

        # Ces compteurs produisent des identifiants temporaires uniques.
        self._next_niveau_id = 1
        self._next_eleve_id = 1

    # ------------------------------------------------------------------
    # Gestion des niveaux
    # ------------------------------------------------------------------

    def get_niveaux(self) -> list[dict]:
        """
        Récupère niveaux et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        return deepcopy(self._niveaux)

    def get_niveau_by_id(self, niveau_id: int) -> Optional[dict]:
        """
        Récupère niveau by id et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Ajoute niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            nom_niveau : donnée nécessaire au traitement de « nom niveau ».
            matiere : donnée nécessaire au traitement de « matiere ».
            ville : donnée nécessaire au traitement de « ville ».
            etablissement : donnée nécessaire au traitement de « etablissement ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Met à jour niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
            nom_niveau : donnée nécessaire au traitement de « nom niveau ».
            matiere : donnée nécessaire au traitement de « matiere ».
            ville : donnée nécessaire au traitement de « ville ».
            etablissement : donnée nécessaire au traitement de « etablissement ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        for niveau in self._niveaux:
            if niveau["id"] == niveau_id:
                niveau["nom_niveau"] = nom_niveau
                niveau["matiere"] = matiere
                niveau["ville"] = ville
                niveau["etablissement"] = etablissement
                return True

        return False

    def delete_niveau(self, niveau_id: int) -> bool:
        """
        Supprime niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        if self.niveau_has_eleves(niveau_id):
            return False

        for index, niveau in enumerate(self._niveaux):
            if niveau["id"] == niveau_id:
                del self._niveaux[index]
                return True

        return False

    def niveau_has_eleves(self, niveau_id: int) -> bool:
        """
        Effectue le traitement correspondant à niveau has eleves dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        return any(
            eleve["niveau_id"] == niveau_id
            for eleve in self._eleves
        )

    def niveau_name_exists(
        self,
        nom_niveau: str,
        etablissement: str,
        ignored_niveau_id: Optional[int] = None,) -> bool:
        """
        Effectue le traitement correspondant à niveau name exists dans le contexte de cette fenêtre.
        
        Paramètres :
            nom_niveau : donnée nécessaire au traitement de « nom niveau ».
            etablissement : donnée nécessaire au traitement de « etablissement ».
            ignored_niveau_id : donnée nécessaire au traitement de « ignored niveau id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Récupère eleves et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        return deepcopy(self._eleves)

    def get_eleve_by_id(self, eleve_id: int) -> Optional[dict]:
        """
        Récupère eleve by id et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            eleve_id : identifiant de l’élève concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Ajoute eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            nom_eleve : donnée nécessaire au traitement de « nom eleve ».
            prenom : donnée nécessaire au traitement de « prenom ».
            date_naissance : donnée nécessaire au traitement de « date naissance ».
            redoublant : donnée nécessaire au traitement de « redoublant ».
            ville : donnée nécessaire au traitement de « ville ».
            cp : donnée nécessaire au traitement de « cp ».
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Met à jour eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            eleve_id : identifiant de l’élève concerné.
            nom_eleve : donnée nécessaire au traitement de « nom eleve ».
            prenom : donnée nécessaire au traitement de « prenom ».
            date_naissance : donnée nécessaire au traitement de « date naissance ».
            redoublant : donnée nécessaire au traitement de « redoublant ».
            ville : donnée nécessaire au traitement de « ville ».
            cp : donnée nécessaire au traitement de « cp ».
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Supprime eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            eleve_id : identifiant de l’élève concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        for index, eleve in enumerate(self._eleves):
            if eleve["id"] == eleve_id:
                del self._eleves[index]
                return True

        return False

    def get_eleves_by_niveau(self, niveau_id: int) -> list[dict]:
        """
        Récupère eleves by niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        return [
            deepcopy(eleve)
            for eleve in self._eleves
            if eleve["niveau_id"] == niveau_id
        ]
