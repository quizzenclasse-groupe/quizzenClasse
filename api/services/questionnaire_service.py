# api/services/questionnaire_service.py
"""
Service métier pour les questionnaires (QCM).

Adapté de `database/features/management_quest.py::ManagementQuestionnaire`,
dont on reprend la logique de contrôle de droits
(`_verifier_droits_sur_questionnaire`) en la reliant aux repositories
réels de cette API plutôt qu'aux objets `*BD` abstraits qui n'étaient
pas implémentés dans le projet d'origine.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from api.repositories.questionnaire_repository import QuestionnaireRepository
from api.schemas.questionnaire import (
    QuestionCreation,
    QuestionnaireCreation,
    QuestionnaireMiseAJour,
    PropositionCreation,
)
from api.security import est_admin
from database.models.models_evaluation import Proposition, Question, Questionnaire
from database.models.models_utilisateurs import Utilisateur


class QuestionnaireService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = QuestionnaireRepository(session)

    # -- Lecture ----------------------------------------------------------

    def lister_pour(self, enseignant: Utilisateur) -> list[Questionnaire]:
        if est_admin(enseignant):
            return self.repo.lister()
        return self.repo.par_auteur(enseignant.id)

    def obtenir(self, questionnaire_id: int) -> Questionnaire:
        questionnaire = self.repo.obtenir(questionnaire_id)
        if questionnaire is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire introuvable.",
            )
        return questionnaire

    def _verifier_droits(self, questionnaire: Questionnaire, utilisateur: Utilisateur) -> None:
        """Reprend la règle de `_verifier_droits_sur_questionnaire` de l'ancien contrôleur."""
        if est_admin(utilisateur):
            return
        if questionnaire.auteur_id != utilisateur.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez agir que sur vos propres questionnaires.",
            )

    # -- Écriture -----------------------------------------------------------

    def creer(self, donnees: QuestionnaireCreation, enseignant: Utilisateur) -> Questionnaire:
        """
        Crée un questionnaire, éventuellement avec ses questions et
        propositions imbriquées en une seule requête (cf. schéma
        `QuestionnaireCreation`).
        """
        questionnaire = Questionnaire(
            titre=donnees.titre.strip(),
            niveau=donnees.niveau,
            matiere=donnees.matiere,
            difficulte=donnees.difficulte,
            auteur_id=enseignant.id,
        )

        for q in donnees.questions:
            questionnaire.questions.append(self._construire_question(q))

        return self.repo.ajouter(questionnaire)

    @staticmethod
    def _construire_question(donnees: QuestionCreation) -> Question:
        question = Question(
            enonce=donnees.enonce,
            type_question=donnees.type_question,
        )
        question.propositions = [
            Proposition(libelle=p.libelle, est_correcte=p.est_correcte)
            for p in donnees.propositions
        ]
        return question

    def modifier(
        self,
        questionnaire_id: int,
        donnees: QuestionnaireMiseAJour,
        utilisateur: Utilisateur,
    ) -> Questionnaire:
        questionnaire = self.obtenir(questionnaire_id)
        self._verifier_droits(questionnaire, utilisateur)

        for champ, valeur in donnees.model_dump(exclude_none=True).items():
            setattr(questionnaire, champ, valeur)

        return self.repo.sauvegarder(questionnaire)

    def supprimer(self, questionnaire_id: int, utilisateur: Utilisateur) -> None:
        questionnaire = self.obtenir(questionnaire_id)
        self._verifier_droits(questionnaire, utilisateur)
        self.repo.supprimer(questionnaire)

    def ajouter_question(
        self, questionnaire_id: int, donnees: QuestionCreation, utilisateur: Utilisateur
    ) -> Questionnaire:
        questionnaire = self.obtenir(questionnaire_id)
        self._verifier_droits(questionnaire, utilisateur)

        question = self._construire_question(donnees)

        try:
            # Réutilisation de la méthode métier existante, qui empêche
            # déjà les doublons dans la liste de questions.
            questionnaire.ajouterQuestion(question)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        return self.repo.sauvegarder(questionnaire)

    def retirer_question(
        self, questionnaire_id: int, question_id: int, utilisateur: Utilisateur
    ) -> Questionnaire:
        questionnaire = self.obtenir(questionnaire_id)
        self._verifier_droits(questionnaire, utilisateur)

        question = next(
            (q for q in questionnaire.questions if q.id == question_id), None
        )
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cette question n'appartient pas à ce questionnaire.",
            )

        questionnaire.questions.remove(question)
        return self.repo.sauvegarder(questionnaire)

    def ajouter_proposition(
        self,
        questionnaire_id: int,
        question_id: int,
        donnees: PropositionCreation,
        utilisateur: Utilisateur,
    ) -> Question:
        questionnaire = self.obtenir(questionnaire_id)
        self._verifier_droits(questionnaire, utilisateur)

        question = next(
            (q for q in questionnaire.questions if q.id == question_id), None
        )
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cette question n'appartient pas à ce questionnaire.",
            )

        proposition = Proposition(
            libelle=donnees.libelle, est_correcte=donnees.est_correcte
        )

        try:
            question.ajouterProposition(proposition)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        self.session.commit()
        self.session.refresh(question)
        return question
