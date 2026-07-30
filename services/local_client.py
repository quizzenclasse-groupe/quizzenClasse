# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Client local de démonstration reproduisant les opérations principales.

"""Client local utilisé pour tester la GUI sans lancer l'API.

Il reprend les mêmes méthodes que ``ApiClient`` afin que les fenêtres
ne sachent pas si les données viennent du réseau ou de la mémoire.

Ce mode local ne couvre que les questionnaires, les sessions et les
participations : il n'a jamais implémenté les niveaux/élèves/équipes/cours
(pas de list_niveaux, list_eleves, etc.). C'est suffisant pour tester
rapidement l'écran sessions sans lancer le serveur, mais ce client ne peut
pas remplacer l'API pour un test complet de l'application. Voir le rapport,
section limites connues. Dans la version remise, USE_API vaut True dans
config.py donc ce client n'est de toute façon pas utilisé.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class LocalClient:
    """Version "hors ligne" très partielle d'ApiClient, pour dépanner sans serveur lancé."""

    def __init__(self) -> None:
        self.token = "mode-local"
        self._questionnaire_id = 1
        self._session_id = 1
        self._participation_id = 1
        self._questionnaires: list[dict] = []
        self._sessions: list[dict] = []
        self._participations: list[dict] = []

    def login(self, _username: str, _password: str) -> None:
        # Pas d'auth en local, on accepte tout le monde.
        pass

    def get_profile(self) -> dict:
        return {
            "id": 0,
            "nom": "Enseignant de test",
            "nom_utilisateur": "local",
            "nom_etablissement": "Mode hors ligne",
        }

    # Questionnaires -------------------------------------------------
    def list_questionnaires(self) -> list[dict]:
        return [self._questionnaire_summary(item) for item in self._questionnaires]

    def get_questionnaire(self, questionnaire_id: int) -> dict | None:
        item = self._find(self._questionnaires, questionnaire_id)
        return deepcopy(item) if item else None

    def create_questionnaire(self, data: dict) -> dict:
        item = deepcopy(data)
        item["id"] = self._questionnaire_id
        self._questionnaire_id += 1
        self._questionnaires.append(item)
        return deepcopy(item)

    def update_questionnaire(self, questionnaire_id: int, data: dict) -> dict | None:
        item = self._find(self._questionnaires, questionnaire_id)
        if item:
            item.update(deepcopy(data))
            return deepcopy(item)
        return None

    def delete_questionnaire(self, questionnaire_id: int) -> None:
        self._questionnaires = [
            item for item in self._questionnaires if item["id"] != questionnaire_id
        ]

    # Sessions -------------------------------------------------------
    def create_session(self, data: dict) -> dict:
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
        return deepcopy([
            item for item in self._sessions
            if item["questionnaire_id"] == questionnaire_id
        ])

    def start_session(self, session_id: int) -> dict | None:
        item = self._find(self._sessions, session_id)
        if item:
            item["statut"] = "en_cours"
            item["date_debut"] = self._now()
            return deepcopy(item)
        return None

    def close_session(self, session_id: int) -> dict | None:
        item = self._find(self._sessions, session_id)
        if item:
            item["statut"] = "terminee"
            item["date_fin"] = self._now()
            return deepcopy(item)
        return None

    def get_share_code(self, session_id: int) -> dict:
        item = self._find(self._sessions, session_id)
        return {"code": item["code"] if item else "—"}

    def get_statistics(self, _session_id: int) -> dict:
        # Pas de vraie moyenne calculée en local, ça reste à 0.
        return {
            "nombre_participations": 0,
            "nombre_participations_evaluees": 0,
            "moyenne": 0.0,
            "score_minimum": None,
            "score_maximum": None,
            "taux_reussite": 0.0,
        }

    def get_report(self, session_id: int) -> dict:
        return self.get_statistics(session_id)

    @staticmethod
    def _find(items: list[dict], item_id: int) -> dict | None:
        return next((item for item in items if item["id"] == item_id), None)

    @staticmethod
    def _questionnaire_summary(item: dict) -> dict:
        summary = deepcopy(item)
        summary["nombre_questions"] = len(item.get("questions", []))
        return summary

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    # Participations ---------------------------------------------------
    # Stockées directement ici (comme les questionnaires et les sessions
    # au-dessus), pas via un DataStore externe : plus simple à tester seul.
    def list_participations(self, session_id: int):
        return deepcopy([
            item for item in self._participations
            if item["session_id"] == session_id
        ])

    def create_participation(self, session_id: int, data: dict):
        item = deepcopy(data)
        item.update({
            "id": self._participation_id,
            "session_id": session_id,
            "score": None,
            "commentaire_final": None,
        })
        self._participation_id += 1
        self._participations.append(item)
        return deepcopy(item)

    def evaluate_participation(self, participation_id: int, data: dict):
        item = self._find(self._participations, participation_id)
        if item:
            item.update(deepcopy(data))
            return deepcopy(item)
        return None
