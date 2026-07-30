# api/routers/questionnaire_router.py
# Rôle : Routes HTTP pour les questionnaires (QCM), questions et propositions.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from api.deps import get_db
from api.schemas.questionnaire import (
    PropositionCreation,
    PropositionPublic,
    QuestionCreation,
    QuestionPublic,
    QuestionnaireCreation,
    QuestionnaireEnBref,
    QuestionnaireMiseAJour,
    QuestionnairePublic,
)
from api.security import get_current_enseignant
from api.services.questionnaire_service import QuestionnaireService
from database.models.models_utilisateurs import Enseignant

router = APIRouter(prefix="/api/questionnaires", tags=["Questionnaires"])


@router.get("", response_model=list[QuestionnaireEnBref], summary="Lister mes questionnaires")
def lister_questionnaires(
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> list[QuestionnaireEnBref]:
    questionnaires = QuestionnaireService(db).lister_pour(enseignant)
    return [QuestionnaireEnBref.depuis_orm(q) for q in questionnaires]


@router.post(
    "",
    response_model=QuestionnairePublic,
    status_code=201,
    summary="Créer un questionnaire (avec questions/propositions imbriquées, optionnel)",
)
def creer_questionnaire(
    donnees: QuestionnaireCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionnairePublic:
    questionnaire = QuestionnaireService(db).creer(donnees, enseignant)
    return QuestionnairePublic.model_validate(questionnaire)


@router.get(
    "/{questionnaire_id}",
    response_model=QuestionnairePublic,
    summary="Détail complet d'un questionnaire (questions + propositions)",
)
def obtenir_questionnaire(
    questionnaire_id: int,
    db: OrmSession = Depends(get_db),
    _enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionnairePublic:
    questionnaire = QuestionnaireService(db).obtenir(questionnaire_id)
    return QuestionnairePublic.model_validate(questionnaire)


@router.patch(
    "/{questionnaire_id}",
    response_model=QuestionnairePublic,
    summary="Modifier les métadonnées d'un questionnaire",
)
def modifier_questionnaire(
    questionnaire_id: int,
    donnees: QuestionnaireMiseAJour,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionnairePublic:
    questionnaire = QuestionnaireService(db).modifier(questionnaire_id, donnees, enseignant)
    return QuestionnairePublic.model_validate(questionnaire)


@router.delete("/{questionnaire_id}", status_code=204, response_model=None, summary="Supprimer un questionnaire")
def supprimer_questionnaire(
    questionnaire_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> None:
    QuestionnaireService(db).supprimer(questionnaire_id, enseignant)


@router.post(
    "/{questionnaire_id}/questions",
    response_model=QuestionnairePublic,
    status_code=201,
    summary="Ajouter une question (avec propositions imbriquées, optionnel)",
)
def ajouter_question(
    questionnaire_id: int,
    donnees: QuestionCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionnairePublic:
    questionnaire = QuestionnaireService(db).ajouter_question(
        questionnaire_id, donnees, enseignant
    )
    return QuestionnairePublic.model_validate(questionnaire)


@router.delete(
    "/{questionnaire_id}/questions/{question_id}",
    response_model=QuestionnairePublic,
    summary="Retirer une question d'un questionnaire",
)
def retirer_question(
    questionnaire_id: int,
    question_id: int,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionnairePublic:
    questionnaire = QuestionnaireService(db).retirer_question(
        questionnaire_id, question_id, enseignant
    )
    return QuestionnairePublic.model_validate(questionnaire)


@router.post(
    "/{questionnaire_id}/questions/{question_id}/propositions",
    response_model=QuestionPublic,
    status_code=201,
    summary="Ajouter une proposition de réponse à une question",
)
def ajouter_proposition(
    questionnaire_id: int,
    question_id: int,
    donnees: PropositionCreation,
    db: OrmSession = Depends(get_db),
    enseignant: Enseignant = Depends(get_current_enseignant),
) -> QuestionPublic:
    question = QuestionnaireService(db).ajouter_proposition(
        questionnaire_id, question_id, donnees, enseignant
    )
    return QuestionPublic.model_validate(question)
