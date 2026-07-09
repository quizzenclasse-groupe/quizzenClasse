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


def test_participation_enregistre_score_et_commentaires():
    participation = Participation(
        session_questionnaire_id=1,
        participant_id=1,
    )

    participation.evaluer(
        score=8.0,
        commentaire_initial="Participation sérieuse.",
        commentaire_final="Résultat satisfaisant.",
    )

    assert participation.score == 8.0
    assert participation.commentaire_initial == "Participation sérieuse."
    assert participation.commentaire_final == "Résultat satisfaisant."


def test_participation_refuse_un_score_negatif():
    participation = Participation(
        session_questionnaire_id=1,
        participant_id=1,
    )

    with pytest.raises(ValueError, match="négatif"):
        participation.evaluer(score=-1.0)

