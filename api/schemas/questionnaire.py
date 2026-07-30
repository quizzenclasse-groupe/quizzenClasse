# api/schemas/questionnaire.py
"""
Schémas Pydantic pour les questionnaires (QCM), leurs questions et les
propositions de réponse associées.

Ces trois entités forment une hiérarchie imbriquée
(Questionnaire -> Question -> Proposition). On expose donc :
  - des schémas de CRÉATION "profonds" (un questionnaire peut être créé
    directement avec toutes ses questions et propositions en une seule
    requête, pour limiter les allers-retours réseau côté frontend) ;
  - un schéma de LECTURE imbriqué équivalent, pour l'affichage détaillé ;
  - des schémas plus légers pour les opérations ciblées (ajouter UNE
    question à un questionnaire existant, par exemple).
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ----------------------------------------------------------------------------
# Propositions
# ----------------------------------------------------------------------------


class PropositionCreation(BaseModel):
    libelle: str = Field(min_length=1, max_length=500)
    est_correcte: bool = False


class PropositionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str
    est_correcte: bool


# ----------------------------------------------------------------------------
# Questions
# ----------------------------------------------------------------------------


class QuestionCreation(BaseModel):
    enonce: str = Field(min_length=1, max_length=500)
    type_question: str = "QCM"
    propositions: list[PropositionCreation] = Field(default_factory=list)

    @model_validator(mode="after")
    def _verifier_au_moins_une_bonne_reponse(self) -> "QuestionCreation":
        """
        Règle métier ajoutée côté API (absente du modèle ORM d'origine,
        qui ne validait pas cette contrainte) : un QCM sans aucune bonne
        réponse n'a pas de sens pédagogique. On la vérifie uniquement
        quand des propositions sont fournies à la création, pour ne pas
        bloquer la création d'une question "à compléter plus tard".
        """
        if self.propositions and not any(
            p.est_correcte for p in self.propositions
        ):
            raise ValueError(
                "Au moins une proposition doit être marquée comme correcte."
            )
        return self


class QuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enonce: str
    type_question: str
    propositions: list[PropositionPublic] = Field(default_factory=list)


# ----------------------------------------------------------------------------
# Questionnaires
# ----------------------------------------------------------------------------


class QuestionnaireCreation(BaseModel):
    titre: str = Field(min_length=1, max_length=200)
    niveau: str | None = None
    matiere: str | None = None
    difficulte: str | None = None
    questions: list[QuestionCreation] = Field(default_factory=list)


class QuestionnaireMiseAJour(BaseModel):
    titre: str | None = None
    niveau: str | None = None
    matiere: str | None = None
    difficulte: str | None = None


class QuestionnairePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titre: str
    niveau: str | None = None
    matiere: str | None = None
    difficulte: str | None = None
    date_creation: date
    auteur_id: int
    questions: list[QuestionPublic] = Field(default_factory=list)


class QuestionnaireEnBref(BaseModel):
    """Vue allégée utilisée dans les listes (sans le détail des questions)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    titre: str
    matiere: str | None = None
    difficulte: str | None = None
    date_creation: date
    nombre_questions: int = 0

    @classmethod
    def depuis_orm(cls, questionnaire) -> "QuestionnaireEnBref":
        return cls(
            id=questionnaire.id,
            titre=questionnaire.titre,
            matiere=questionnaire.matiere,
            difficulte=questionnaire.difficulte,
            date_creation=questionnaire.date_creation,
            nombre_questions=len(questionnaire.questions),
        )
