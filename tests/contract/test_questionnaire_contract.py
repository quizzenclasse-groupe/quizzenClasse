# tests/contract/test_questionnaire_contract.py
# *******************************************************
# Nom ......... : test_questionnaire_contract.py
# Rôle ........ : Vérifie le contrat fonctionnel d'un
#                 questionnaire QCM, notamment le nombre de
#                 questions, le nombre de propositions et
#                 l'unicité de la bonne réponse.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 tests/contract/test_questionnaire_contract.py
# Usage ....... : Pour exécuter ce fichier de tests :
#                 python -m pytest \
#                 tests/contract/test_questionnaire_contract.py -q
# *******************************************************
from __future__ import annotations

import pytest

from database.services.connexion_service import ConnexionService
from tests.factories import (
    QCM_MATHEMATIQUES,
    creer_questionnaire_math,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.contract,
]


def test_qcm_contient_dix_questions_et_quatre_propositions_par_question(
    session,
):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.qcm",
        "MotDePasse-2026",
    )

    questionnaire = creer_questionnaire_math(enseignant)

    assert len(questionnaire.questions) == 10
    assert all(
        len(question.propositions) == 4
        for question in questionnaire.questions
    )


def test_chaque_question_possede_une_seule_bonne_reponse(session):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.reponses",
        "MotDePasse-2026",
    )

    questionnaire = creer_questionnaire_math(enseignant)

    for question in questionnaire.questions:
        propositions_correctes = [
            proposition
            for proposition in question.propositions
            if proposition.est_correcte
        ]
        assert len(propositions_correctes) == 1


def test_contenu_du_qcm_est_deterministe():
    assert len(QCM_MATHEMATIQUES) == 10
    assert QCM_MATHEMATIQUES[0].index_correct == 1
    assert QCM_MATHEMATIQUES[-1].index_correct == 1
