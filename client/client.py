# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Client HTTP centralisant les échanges avec les services du projet.

"""Client HTTP unique utilisé par toute l'interface Tkinter.

Le code réseau reste ici afin que les fenêtres ne connaissent ni urllib,
ni les en-têtes HTTP, ni le format des erreurs renvoyées par FastAPI.
Les méthodes ci-dessous sont volontairement de simples wrappers autour de
``_request`` : un commentaire d'une ligne suffit pour chacune, la vraie
logique (gestion des erreurs, du token, etc.) est dans ``_request``.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiError(Exception):
    """Erreur levée quand l'API renvoie un statut HTTP d'erreur ou est injoignable."""


class ApiClient:
    """Client HTTP vers l'API FastAPI du projet (authentification par token Bearer)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None
        # Cache partagé avec les fenêtres GUI pour éviter de rechercher un
        # établissement plusieurs fois (utilisé par NiveauSection notamment).
        self.etablissement_names_by_id: dict[int, str] = {}

    def _request(self, method: str, path: str, data=None):
        """Envoie une requête HTTP à l'API et renvoie le JSON décodé (ou lève une ``ApiError``).

        Toutes les autres méthodes de la classe passent par ici : c'est le
        seul endroit où le token, les en-têtes et les erreurs HTTP sont gérés.

        Paramètres :
            method : verbe HTTP (``"GET"``, ``"POST"``, ``"PATCH"``, ``"DELETE"``).
            path : chemin de la route, ex. ``"/api/niveaux"``.
            data : corps de la requête, sérialisé en JSON si fourni.

        Retour :
            Le JSON décodé de la réponse, ``True`` pour un ``DELETE`` sans
            corps de réponse, ou ``None`` si la réponse est vide.
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
        """Extrait un message lisible du corps JSON d'une erreur HTTP renvoyée par FastAPI.

        FastAPI renvoie parfois un simple texte dans ``detail``, parfois une
        liste d'erreurs de validation Pydantic : les deux cas sont gérés ici.
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
        """Authentifie l'utilisateur et stocke le token reçu dans ``self.token``.

        Route à part par rapport à ``_request`` car FastAPI attend ici un
        corps ``application/x-www-form-urlencoded`` (format OAuth2) et non
        du JSON comme les autres routes de l'API.
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
        # Crée un compte enseignant.
        return self._request("POST", "/api/auth/register", data)

    def get_profile(self):
        # Récupère le profil de l'enseignant actuellement connecté (token courant).
        return self._request("GET", "/api/auth/moi")

    # Parcours scolaire
    def search_etablissements(self, query: str):
        """Recherche des établissements par nom et alimente le cache partagé ``etablissement_names_by_id``."""
        results = self._request("GET", f"/api/etablissements?{urlencode({'q': query})}")
        for item in results or []:
            if item.get("id") is not None and item.get("nom_etablissement"):
                self.etablissement_names_by_id[item["id"]] = item["nom_etablissement"]
        return results

    def list_niveaux(self):
        # Liste les niveaux de l'enseignant connecté.
        return self._request("GET", "/api/niveaux")

    def create_niveau(self, data: dict):
        return self._request("POST", "/api/niveaux", data)

    def update_niveau(self, niveau_id: int, data: dict):
        return self._request("PATCH", f"/api/niveaux/{niveau_id}", data)

    def delete_niveau(self, niveau_id: int):
        return self._request("DELETE", f"/api/niveaux/{niveau_id}")

    def list_eleves(self, niveau_id: int):
        # Liste les élèves d'un niveau donné.
        return self._request("GET", f"/api/niveaux/{niveau_id}/eleves")

    def get_eleve(self, eleve_id: int):
        return self._request("GET", f"/api/eleves/{eleve_id}")

    def create_eleve(self, data: dict):
        return self._request("POST", "/api/eleves", data)

    def update_eleve(self, eleve_id: int, data: dict):
        return self._request("PATCH", f"/api/eleves/{eleve_id}", data)

    # Pas de delete_eleve : la route DELETE correspondante n'existe pas côté
    # API (contrairement à delete_niveau ci-dessus). Voir le rapport.

    def create_equipe(self, data: dict):
        return self._request("POST", "/api/equipes", data)

    def get_equipe(self, equipe_id: int):
        return self._request("GET", f"/api/equipes/{equipe_id}")

    # Cours (CRUD complet côté API, écran GUI non relié au tableau de bord)
    def list_cours(self):
        return self._request("GET", "/api/cours")

    def get_cours(self, cours_id: int):
        return self._request("GET", f"/api/cours/{cours_id}")

    def create_cours(self, data: dict):
        return self._request("POST", "/api/cours", data)

    def update_cours(self, cours_id: int, data: dict):
        return self._request("PATCH", f"/api/cours/{cours_id}", data)

    def delete_cours(self, cours_id: int):
        return self._request("DELETE", f"/api/cours/{cours_id}")

    # Questionnaires
    def list_questionnaires(self):
        return self._request("GET", "/api/questionnaires")

    def get_questionnaire(self, questionnaire_id: int):
        return self._request("GET", f"/api/questionnaires/{questionnaire_id}")

    def create_questionnaire(self, data: dict):
        # data peut contenir une liste "questions" pour créer le questionnaire
        # avec son contenu en un seul appel (voir QuestionnairesWindow.save).
        return self._request("POST", "/api/questionnaires", data)

    def update_questionnaire(self, questionnaire_id: int, data: dict):
        # Ne modifie que les métadonnées (titre, niveau, matière, difficulté).
        return self._request("PATCH", f"/api/questionnaires/{questionnaire_id}", data)

    def delete_questionnaire(self, questionnaire_id: int):
        return self._request("DELETE", f"/api/questionnaires/{questionnaire_id}")

    def add_question(self, questionnaire_id: int, data: dict):
        return self._request("POST", f"/api/questionnaires/{questionnaire_id}/questions", data)

    def add_proposition(self, questionnaire_id: int, question_id: int, data: dict):
        return self._request(
            "POST",
            f"/api/questionnaires/{questionnaire_id}/questions/{question_id}/propositions",
            data,
        )

    def delete_question(self, questionnaire_id: int, question_id: int):
        return self._request(
            "DELETE",
            f"/api/questionnaires/{questionnaire_id}/questions/{question_id}",
        )

    # Sessions et rapports
    def create_session(self, data: dict):
        return self._request("POST", "/api/sessions", data)

    def list_sessions(self, questionnaire_id: int):
        return self._request("GET", f"/api/questionnaires/{questionnaire_id}/sessions")

    def start_session(self, session_id: int):
        return self._request("POST", f"/api/sessions/{session_id}/demarrer")

    def close_session(self, session_id: int):
        return self._request("POST", f"/api/sessions/{session_id}/cloturer")

    def get_share_code(self, session_id: int):
        return self._request("GET", f"/api/sessions/{session_id}/code-partage")

    def get_statistics(self, session_id: int):
        return self._request("GET", f"/api/sessions/{session_id}/statistiques")

    def get_report(self, session_id: int):
        return self._request("GET", f"/api/sessions/{session_id}/rapport")

    # Accès public élève / correction automatique
    def open_public_session(self, session_id: int, code: str):
        # Route publique (pas de token) protégée par le code de partage.
        return self._request("GET", f"/api/public/sessions/{session_id}/{code}")

    def submit_public_answers(self, session_id: int, code: str, data: dict):
        # Envoie les réponses d'un participant ; la correction (score, bonnes
        # réponses) est calculée côté serveur et renvoyée dans la réponse.
        return self._request(
            "POST",
            f"/api/public/sessions/{session_id}/{code}/reponses",
            data,
        )

    # Participations

    def list_participations(self, session_id: int):
        return self._request("GET", f"/api/sessions/{session_id}/participations")

    def create_participation(self, session_id: int, data: dict):
        return self._request(
            "POST",
            f"/api/sessions/{session_id}/participations",
            data,
        )

    def evaluate_participation(self, participation_id: int, data: dict):
        # Enregistre le score et le commentaire final saisis par l'enseignant.
        return self._request(
            "PATCH",
            f"/api/participations/{participation_id}/evaluer",
            data,
        )
