# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Client local de démonstration reproduisant les opérations principales.

"""Client local utilisé pour tester la GUI sans lancer l'API.

Il reprend les mêmes méthodes que ``ApiClient`` afin que les fenêtres
ne sachent pas si les données viennent du réseau ou de la mémoire.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class LocalClient:
    """
    Représente local client dans l'interface graphique QuizzenClasse.
    
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
        self.token = "mode-local"
        self._questionnaire_id = 1
        self._session_id = 1
        self._questionnaires: list[dict] = []
        self._sessions: list[dict] = []

    def login(self, _username: str, _password: str) -> None:
        """
        Vérifie les informations saisies, demande l'authentification de l'utilisateur et ouvre le tableau de bord en cas de réussite.
        
        Paramètres :
            _username : donnée nécessaire au traitement de « username ».
            _password : donnée nécessaire au traitement de « password ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

    def get_profile(self) -> dict:
        """
        Récupère profile et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return {
            "id": 0,
            "nom": "Enseignant de test",
            "nom_utilisateur": "local",
            "nom_etablissement": "Mode hors ligne",
        }

    # Questionnaires -------------------------------------------------
    def list_questionnaires(self) -> list[dict]:
        """
        Récupère la liste de questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return [self._questionnaire_summary(item) for item in self._questionnaires]

    def get_questionnaire(self, questionnaire_id: int) -> dict | None:
        """
        Récupère questionnaire et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = self._find(self._questionnaires, questionnaire_id)
        return deepcopy(item) if item else None

    def create_questionnaire(self, data: dict) -> dict:
        """
        Crée questionnaire et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = deepcopy(data)
        item["id"] = self._questionnaire_id
        self._questionnaire_id += 1
        self._questionnaires.append(item)
        return deepcopy(item)

    def update_questionnaire(self, questionnaire_id: int, data: dict) -> dict | None:
        """
        Met à jour questionnaire et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = self._find(self._questionnaires, questionnaire_id)
        if item:
            item.update(deepcopy(data))
            return deepcopy(item)
        return None

    def delete_questionnaire(self, questionnaire_id: int) -> None:
        """
        Supprime questionnaire et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self._questionnaires = [
            item for item in self._questionnaires if item["id"] != questionnaire_id
        ]

    # Sessions -------------------------------------------------------
    def create_session(self, data: dict) -> dict:
        """
        Crée session et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = deepcopy(data)
        item.update({
            "id": self._session_id,
            "statut": "preparee",
            "date_debut": None,
            "date_fin": None,
            "code": f"LOCAL{self._session_id:03d}",
        })
        self._session_id += 1
        self._sessions.append(item)
        return deepcopy(item)

    def list_sessions(self, questionnaire_id: int) -> list[dict]:
        """
        Récupère la liste de sessions et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return deepcopy([
            item for item in self._sessions
            if item["questionnaire_id"] == questionnaire_id
        ])

    def start_session(self, session_id: int) -> dict | None:
        """
        Démarre session et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = self._find(self._sessions, session_id)
        if item:
            item["statut"] = "en_cours"
            item["date_debut"] = self._now()
            return deepcopy(item)
        return None

    def close_session(self, session_id: int) -> dict | None:
        """
        Effectue le traitement correspondant à close session dans le contexte de cette fenêtre.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = self._find(self._sessions, session_id)
        if item:
            item["statut"] = "terminee"
            item["date_fin"] = self._now()
            return deepcopy(item)
        return None

    def get_share_code(self, session_id: int) -> dict:
        """
        Récupère share code et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item = self._find(self._sessions, session_id)
        return {"code": item["code"] if item else "—"}

    def get_statistics(self, _session_id: int) -> dict:
        """
        Récupère statistics et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _session_id : donnée nécessaire au traitement de « session id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        return {
            "nombre_participations": 0,
            "nombre_participations_evaluees": 0,
            "moyenne": 0.0,
            "score_minimum": None,
            "score_maximum": None,
            "taux_reussite": 0.0,
        }

    def get_report(self, session_id: int) -> dict:
        """
        Récupère report et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self.get_statistics(session_id)

    @staticmethod
    def _find(items: list[dict], item_id: int) -> dict | None:
        """
        Effectue le traitement correspondant à find dans le contexte de cette fenêtre.
        
        Paramètres :
            items : donnée nécessaire au traitement de « items ».
            item_id : donnée nécessaire au traitement de « item id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return next((item for item in items if item["id"] == item_id), None)

    @staticmethod
    def _questionnaire_summary(item: dict) -> dict:
        """
        Effectue le traitement correspondant à questionnaire summary dans le contexte de cette fenêtre.
        
        Paramètres :
            item : donnée nécessaire au traitement de « item ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        summary = deepcopy(item)
        summary["nombre_questions"] = len(item.get("questions", []))
        return summary

    @staticmethod
    def _now() -> str:
        """
        Effectue le traitement correspondant à now dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M")


    # Participations

    def list_participations(self, session_id: int):
        """
        Récupère la liste de participations et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self.data_store.list_participations(session_id)

    def create_participation(self, session_id: int, data: dict):
        """
        Crée participation et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self.data_store.create_participation(session_id, data)

    def evaluate_participation(self, participation_id: int, data: dict):
        """
        Effectue le traitement correspondant à evaluate participation dans le contexte de cette fenêtre.
        
        Paramètres :
            participation_id : donnée nécessaire au traitement de « participation id ».
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self.data_store.evaluate_participation(participation_id, data)
