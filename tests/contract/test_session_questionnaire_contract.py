from __future__ import annotations

import pytest

from database.models.models_participants import Participation
from database.services.connexion_service import ConnexionService
from tests.factories import (
    calculer_score,
    creer_questionnaire_math,
    creer_session_questionnaire,
    simuler_reponses,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.contract,
]


def test_cycle_de_vie_d_une_session(session):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.session",
        "MotDePasse-2026",
    )
    questionnaire = creer_questionnaire_math(enseignant)
    session_questionnaire = creer_session_questionnaire(
        questionnaire=questionnaire,
        titre="Session Première S",
    )

    assert hasattr(session_questionnaire, "lancer")
    assert hasattr(session_questionnaire, "clore")

    session_questionnaire.lancer()
    assert session_questionnaire.date_debut is not None
    assert session_questionnaire.date_fin is None

    session_questionnaire.clore()
    assert session_questionnaire.date_fin is not None
