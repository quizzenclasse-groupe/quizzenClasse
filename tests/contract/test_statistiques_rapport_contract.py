# tests/contract/test_statistiques_rapport_contract.py
# *******************************************************
# Nom ......... : test_statistiques_rapport_contract.py
# Rôle ........ : Vérifie le calcul des statistiques d'une
#                 session et la génération d'un rapport à
#                 partir d'un jeu déterministe de scores.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 tests/contract/test_statistiques_rapport_contract.py
# Usage ....... : Pour exécuter ce fichier de tests :
#                 python -m pytest \
#                 tests/contract/test_statistiques_rapport_contract.py -q
# *******************************************************
from __future__ import annotations

from statistics import mean

import pytest

from database.models.models_participants import Participation
from tests.factories import charger_classes_evaluation


pytestmark = [
    pytest.mark.unit,
    pytest.mark.contract,
]


def _participations_evaluees() -> list[Participation]:
    scores = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    participations: list[Participation] = []

    for identifiant, score in enumerate(scores, start=1):
        participation = Participation(
            session_questionnaire_id=1,
            participant_id=identifiant,
        )
        participation.evaluer(score=float(score))
        participations.append(participation)

    return participations


def test_jeu_de_scores_possede_une_moyenne_connue():
    participations = _participations_evaluees()
    scores = [participation.score for participation in participations]

    assert mean(scores) == 5.5
    assert min(scores) == 1.0
    assert max(scores) == 10.0


def test_statistiques_session_calculent_la_moyenne():
    classes = charger_classes_evaluation()
    StatistiquesSession = classes["StatistiquesSession"]
    participations = _participations_evaluees()

    assert hasattr(
        StatistiquesSession,
        "calculerMoyenneSession",
    )

    moyenne = StatistiquesSession.calculerMoyenneSession(
        participations
    )

    assert moyenne == pytest.approx(5.5)


def test_generation_du_rapport_de_session():
    classes = charger_classes_evaluation()
    StatistiquesSession = classes["StatistiquesSession"]
    RapportSession = classes["RapportSession"]
    participations = _participations_evaluees()

    assert hasattr(StatistiquesSession, "genererRapportSession")
    assert hasattr(RapportSession, "generer")

    statistiques = StatistiquesSession.genererRapportSession(
        participations
    )
    rapport = RapportSession.generer(statistiques)

    assert rapport is not None
