# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Client HTTP centralisant les échanges avec les services du projet.

"""Client HTTP unique utilisé par toute l'interface Tkinter.

Le code réseau reste ici afin que les fenêtres ne connaissent ni urllib,
ni les en-têtes HTTP, ni le format des erreurs renvoyées par FastAPI.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiError(Exception):
    """
    Représente api error dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """


class ApiClient:
    """
    Représente api client dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            base_url : donnée nécessaire au traitement de « base url ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None
        self.etablissement_names_by_id: dict[int, str] = {}

    def _request(self, method: str, path: str, data=None):
        """
        Construit et exécute une requête HTTP, puis transforme la réponse ou les erreurs en données utilisables par l'interface.
        
        Paramètres :
            method : donnée nécessaire au traitement de « method ».
            path : donnée nécessaire au traitement de « path ».
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        body = None
        headers = {"Accept": "application/json"}

        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=8) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else (True if method == "DELETE" else None)
        except HTTPError as error:
            message = self._read_error(error)
            raise ApiError(message) from error
        except URLError as error:
            raise ApiError(
                "Service indisponible. Vérifiez que le serveur est lancé sur le port 8000."
            ) from error

    @staticmethod
    def _read_error(error: HTTPError) -> str:
        """
        Effectue le traitement correspondant à read error dans le contexte de cette fenêtre.
        
        Paramètres :
            error : donnée nécessaire au traitement de « error ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        try:
            payload = json.loads(error.read().decode("utf-8"))
            detail = payload.get("detail", "Erreur du service")
            if isinstance(detail, list):
                return "\n".join(item.get("msg", str(item)) for item in detail)
            return str(detail)
        except (ValueError, AttributeError):
            return f"Erreur HTTP {error.code}."

    def login(self, username: str, password: str) -> None:
        """
        Vérifie les informations saisies, demande l'authentification de l'utilisateur et ouvre le tableau de bord en cas de réussite.
        
        Paramètres :
            username : donnée nécessaire au traitement de « username ».
            password : donnée nécessaire au traitement de « password ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        form = urlencode({"username": username, "password": password}).encode()
        request = Request(
            f"{self.base_url}/api/auth/login",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
                self.token = payload["access_token"]
        except HTTPError as error:
            raise ApiError(self._read_error(error)) from error
        except URLError as error:
            raise ApiError("Service indisponible. Lancez le serveur avant la connexion.") from error

    def register(self, data: dict):
        """
        Valide le formulaire d'inscription puis transmet les informations nécessaires à la création d'un compte enseignant.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", "/api/auth/register", data)

    def get_profile(self):
        """
        Récupère profile et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", "/api/auth/moi")

    # Parcours scolaire
    def search_etablissements(self, query: str):
        """
        Recherche etablissements et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            query : donnée nécessaire au traitement de « query ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        results = self._request("GET", f"/api/etablissements?{urlencode({'q': query})}")
        for item in results or []:
            if item.get("id") is not None and item.get("nom_etablissement"):
                self.etablissement_names_by_id[item["id"]] = item["nom_etablissement"]
        return results

    def list_niveaux(self):
        """
        Récupère la liste de niveaux et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", "/api/niveaux")

    def create_niveau(self, data: dict):
        """
        Crée niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", "/api/niveaux", data)

    def update_niveau(self, niveau_id: int, data: dict):
        """
        Met à jour niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("PATCH", f"/api/niveaux/{niveau_id}", data)

    def delete_niveau(self, niveau_id: int):
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
        return self._request("DELETE", f"/api/niveaux/{niveau_id}")

    def list_eleves(self, niveau_id: int):
        """
        Récupère la liste de eleves et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/niveaux/{niveau_id}/eleves")

    def get_eleve(self, eleve_id: int):
        """
        Récupère eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            eleve_id : identifiant de l’élève concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/eleves/{eleve_id}")

    def create_eleve(self, data: dict):
        """
        Crée eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", "/api/eleves", data)

    def update_eleve(self, eleve_id: int, data: dict):
        """
        Met à jour eleve et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            eleve_id : identifiant de l’élève concerné.
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("PATCH", f"/api/eleves/{eleve_id}", data)

    def create_equipe(self, data: dict):
        """
        Crée equipe et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", "/api/equipes", data)

    def get_equipe(self, equipe_id: int):
        """
        Récupère equipe et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            equipe_id : identifiant de l’équipe concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/equipes/{equipe_id}")


    # Cours
    def list_cours(self):
        """
        Récupère la liste de cours et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", "/api/cours")

    def get_cours(self, cours_id: int):
        """
        Récupère cours et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            cours_id : donnée nécessaire au traitement de « cours id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/cours/{cours_id}")

    def create_cours(self, data: dict):
        """
        Crée cours et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", "/api/cours", data)

    def update_cours(self, cours_id: int, data: dict):
        """
        Met à jour cours et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            cours_id : donnée nécessaire au traitement de « cours id ».
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("PATCH", f"/api/cours/{cours_id}", data)

    def delete_cours(self, cours_id: int):
        """
        Supprime cours et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            cours_id : donnée nécessaire au traitement de « cours id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("DELETE", f"/api/cours/{cours_id}")

    # Questionnaires
    def list_questionnaires(self):
        """
        Récupère la liste de questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", "/api/questionnaires")

    def get_questionnaire(self, questionnaire_id: int):
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
        return self._request("GET", f"/api/questionnaires/{questionnaire_id}")

    def create_questionnaire(self, data: dict):
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
        return self._request("POST", "/api/questionnaires", data)

    def update_questionnaire(self, questionnaire_id: int, data: dict):
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
        return self._request("PATCH", f"/api/questionnaires/{questionnaire_id}", data)

    def delete_questionnaire(self, questionnaire_id: int):
        """
        Supprime questionnaire et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("DELETE", f"/api/questionnaires/{questionnaire_id}")

    def add_question(self, questionnaire_id: int, data: dict):
        """
        Ajoute question et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("POST", f"/api/questionnaires/{questionnaire_id}/questions", data)

    def add_proposition(self, questionnaire_id: int, question_id: int, data: dict):
        """
        Ajoute proposition et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
            question_id : donnée nécessaire au traitement de « question id ».
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request(
            "POST",
            f"/api/questionnaires/{questionnaire_id}/questions/{question_id}/propositions",
            data,
        )

    def delete_question(self, questionnaire_id: int, question_id: int):
        """
        Supprime question et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            questionnaire_id : identifiant du questionnaire concerné.
            question_id : donnée nécessaire au traitement de « question id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request(
            "DELETE",
            f"/api/questionnaires/{questionnaire_id}/questions/{question_id}",
        )

    # Sessions et rapports
    def create_session(self, data: dict):
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
        return self._request("POST", "/api/sessions", data)

    def list_sessions(self, questionnaire_id: int):
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
        return self._request("GET", f"/api/questionnaires/{questionnaire_id}/sessions")

    def start_session(self, session_id: int):
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
        return self._request("POST", f"/api/sessions/{session_id}/demarrer")

    def close_session(self, session_id: int):
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
        return self._request("POST", f"/api/sessions/{session_id}/cloturer")

    def get_share_code(self, session_id: int):
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
        return self._request("GET", f"/api/sessions/{session_id}/code-partage")

    def get_statistics(self, session_id: int):
        """
        Récupère statistics et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/sessions/{session_id}/statistiques")

    def get_report(self, session_id: int):
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
        return self._request("GET", f"/api/sessions/{session_id}/rapport")

    # Accès public élève / correction automatique
    def open_public_session(self, session_id: int, code: str):
        """
        Ouvre public session et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
            code : donnée nécessaire au traitement de « code ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request("GET", f"/api/public/sessions/{session_id}/{code}")

    def submit_public_answers(self, session_id: int, code: str, data: dict):
        """
        Envoie public answers et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            session_id : identifiant de la session concernée.
            code : donnée nécessaire au traitement de « code ».
            data : donnée nécessaire au traitement de « data ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self._request(
            "POST",
            f"/api/public/sessions/{session_id}/{code}/reponses",
            data,
        )

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
        return self._request("GET", f"/api/sessions/{session_id}/participations")

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
        return self._request(
            "POST",
            f"/api/sessions/{session_id}/participations",
            data,
        )

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
        return self._request(
            "PATCH",
            f"/api/participations/{participation_id}/evaluer",
            data,
        )

