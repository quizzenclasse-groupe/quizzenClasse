# database/features/management_quest.py
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.models_utilisateurs import Utilisateur, Enseignant
    from database.models.models_evaluation import (
        Questionnaire,
        Question,
        Proposition,
        SessionQuestionnaire,
        RapportSession,
        StatistiquesSession,
    )


class ManagementQuestionnaire:
    """
    Contrôleur d'orchestration pour la gestion des questionnaires,
    des questions, des propositions, des sessions et des rapports.

    Cette classe ne porte pas l'état métier du questionnaire :
    elle vérifie les droits, appelle les méthodes du modèle,
    puis délègue la persistance aux objets *BD / repositories.
    """

    @staticmethod
    def _est_admin(utilisateur: "Utilisateur") -> bool:
        return getattr(utilisateur, "type_utilisateur", None) == "admin"

    def _verifier_droits_sur_questionnaire(
        self,
        utilisateur: "Utilisateur",
        questionnaire: "Questionnaire",
    ) -> None:
        """
        Autorise l'action si l'utilisateur est admin ou auteur du questionnaire.
        """
        if self._est_admin(utilisateur):
            return

        auteur_id = getattr(questionnaire, "auteur_id", None)
        auteur = getattr(questionnaire, "auteur", None)

        if auteur_id == utilisateur.id:
            return
        if auteur is not None and getattr(auteur, "id", None) == utilisateur.id:
            return

        raise PermissionError(
            "Vous ne pouvez agir que sur vos propres questionnaires."
        )

    def _verifier_droits_sur_session(
        self,
        utilisateur: "Utilisateur",
        session: "SessionQuestionnaire",
    ) -> None:
        """
        Autorise l'action si l'utilisateur est admin ou propriétaire de la session.
        """
        if self._est_admin(utilisateur):
            return

        enseignant_id = getattr(session, "enseignant_id", None)
        if enseignant_id == utilisateur.id:
            return

        enseignant = getattr(session, "enseignant", None)
        if enseignant is not None and getattr(enseignant, "id", None) == utilisateur.id:
            return

        raise PermissionError(
            "Vous ne pouvez agir que sur vos propres sessions."
        )

    def chargerQuestionnaire(
        self,
        questionnaire_id: int,
        questionnaire_bd: "QuestionnaireBD",
    ) -> "Questionnaire":
        """
        Charge un questionnaire par identifiant.
        """
        questionnaire = questionnaire_bd.charger(questionnaire_id)
        if questionnaire is None:
            raise ValueError(
                f"Aucun questionnaire ne correspond à l'identifiant {questionnaire_id}."
            )
        return questionnaire

    def creerQuestionnaire(
        self,
        enseignant: "Enseignant",
        questionnaire_bd: "QuestionnaireBD",
        q: "Questionnaire",
    ) -> None:
        """
        Persiste un questionnaire déjà construit.

        La saisie console éventuelle doit se faire dans un helper d'interface,
        pas dans l'entité `Enseignant` ni dans le modèle `Questionnaire`.
        """
        if getattr(q, "auteur", None) is None and getattr(q, "auteur_id", None) is None:
            q.auteur = enseignant
        else:
            self._verifier_droits_sur_questionnaire(enseignant, q)

        questionnaire_bd.sauvegarder(q)

    def modifierQuestionnaire(
        self,
        utilisateur: "Utilisateur",
        questionnaire_bd: "QuestionnaireBD",
        q: "Questionnaire",
    ) -> None:
        """
        Sauvegarde un questionnaire déjà modifié.
        """
        self._verifier_droits_sur_questionnaire(utilisateur, q)
        questionnaire_bd.sauvegarder(q)

    def dupliquerQuestionnaire(
        self,
        enseignant: "Enseignant",
        questionnaire_bd: "QuestionnaireBD",
        q: "Questionnaire",
    ) -> "Questionnaire":
        """
        Duplique un questionnaire et affecte la copie au nouvel auteur.
        """
        self._verifier_droits_sur_questionnaire(enseignant, q)
        copie = q.dupliquer(auteur=enseignant)
        questionnaire_bd.sauvegarder(copie)
        return copie

    def ajouterQuestion(
        self,
        utilisateur: "Utilisateur",
        questionnaire_bd: "QuestionnaireBD",
        q: "Questionnaire",
        question: "Question",
    ) -> None:
        """
        Ajoute une question à un questionnaire.
        """
        self._verifier_droits_sur_questionnaire(utilisateur, q)
        q.ajouterQuestion(question)
        questionnaire_bd.sauvegarder(q)

    def retirerQuestion(
        self,
        utilisateur: "Utilisateur",
        questionnaire_bd: "QuestionnaireBD",
        q: "Questionnaire",
        question: "Question",
    ) -> None:
        """
        Retire une question d'un questionnaire.
        """
        self._verifier_droits_sur_questionnaire(utilisateur, q)
        q.retirerQuestion(question)
        questionnaire_bd.sauvegarder(q)

    def ajouterProposition(
        self,
        utilisateur: "Utilisateur",
        questionnaire_bd: "QuestionnaireBD",
        question: "Question",
        p: "Proposition",
    ) -> None:
        """
        Ajoute une proposition à une question.
        """
        questionnaire = question.questionnaire
        self._verifier_droits_sur_questionnaire(utilisateur, questionnaire)
        question.ajouterProposition(p)
        questionnaire_bd.sauvegarder(questionnaire)

    def retirerProposition(
        self,
        utilisateur: "Utilisateur",
        questionnaire_bd: "QuestionnaireBD",
        question: "Question",
        p: "Proposition",
    ) -> None:
        """
        Retire une proposition d'une question.
        """
        questionnaire = question.questionnaire
        self._verifier_droits_sur_questionnaire(utilisateur, questionnaire)
        question.retirerProposition(p)
        questionnaire_bd.sauvegarder(questionnaire)

    def creerSession(
        self,
        enseignant: "Enseignant",
        session_questionnaire_bd: "SessionQuestionnaireBD",
        q: "Questionnaire",
        titre: str,
        mode: str,
    ) -> "SessionQuestionnaire":
        """
        Crée une session rattachée à un questionnaire.
        """
        self._verifier_droits_sur_questionnaire(enseignant, q)

        session = SessionQuestionnaire.creer(
            questionnaire=q,
            enseignant=enseignant,
            titre=titre,
            mode=mode,
        )
        session_questionnaire_bd.sauvegarder(session)
        return session

    def demarrerSession(
        self,
        utilisateur: "Utilisateur",
        session_questionnaire_bd: "SessionQuestionnaireBD",
        s: "SessionQuestionnaire",
    ) -> None:
        """
        Démarre une session.
        """
        self._verifier_droits_sur_session(utilisateur, s)
        s.lancer()
        session_questionnaire_bd.sauvegarder(s)

    def cloturerSession(
        self,
        utilisateur: "Utilisateur",
        session_questionnaire_bd: "SessionQuestionnaireBD",
        s: "SessionQuestionnaire",
    ) -> None:
        """
        Clôture une session.
        """
        self._verifier_droits_sur_session(utilisateur, s)
        s.clore()
        session_questionnaire_bd.sauvegarder(s)

    def genererRapport(
        self,
        utilisateur: "Utilisateur",
        session_questionnaire_bd: "SessionQuestionnaireBD",
        s: "SessionQuestionnaire",
        statistiques: "StatistiquesSession | None" = None,
    ) -> "RapportSession":
        """
        Génère un rapport de session exploitable en couche présentation.
        """
        self._verifier_droits_sur_session(utilisateur, s)
        rapport = RapportSession.generer_depuis_session(
            s,
            statistiques=statistiques,
        )
        session_questionnaire_bd.sauvegarderRapport(rapport)
        return rapport
