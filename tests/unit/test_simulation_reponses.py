from __future__ import annotations

import pytest

from tests.factories import (
    QCM_MATHEMATIQUES,
    calculer_score,
    simuler_reponses,
)


pytestmark = pytest.mark.unit


def test_simulation_des_reponses_est_deterministe():
    premiere_simulation = simuler_reponses(
        numero_groupe=3,
    )

    seconde_simulation = simuler_reponses(
        numero_groupe=3,
    )

    assert premiere_simulation == seconde_simulation


def test_simulation_produit_une_reponse_par_question():
    reponses = simuler_reponses(
        numero_groupe=0,
    )

    assert len(reponses) == len(QCM_MATHEMATIQUES)
    assert len(reponses) == 10


def test_premier_groupe_obtient_dix_bonnes_reponses():
    reponses = simuler_reponses(
        numero_groupe=0,
    )

    score = calculer_score(reponses)

    assert score == 10.0


def test_quatrieme_groupe_obtient_sept_bonnes_reponses():
    reponses = simuler_reponses(
        numero_groupe=3,
    )

    score = calculer_score(reponses)

    assert score == 7.0


def test_dixieme_groupe_obtient_une_bonne_reponse():
    reponses = simuler_reponses(
        numero_groupe=9,
    )

    score = calculer_score(reponses)

    assert score == 1.0


@pytest.mark.parametrize(
    ("numero_groupe", "score_attendu"),
    [
        (0, 10.0),
        (1, 9.0),
        (2, 8.0),
        (3, 7.0),
        (4, 6.0),
        (5, 5.0),
        (6, 4.0),
        (7, 3.0),
        (8, 2.0),
        (9, 1.0),
    ],
)
def test_score_attendu_pour_chaque_groupe(
    numero_groupe: int,
    score_attendu: float,
):
    reponses = simuler_reponses(
        numero_groupe=numero_groupe,
    )

    score = calculer_score(reponses)

    assert score == score_attendu


def test_calcul_score_refuse_un_nombre_incomplet_de_reponses():
    reponses_incompletes = [0, 1, 2]

    with pytest.raises(
        ValueError,
        match="Une réponse est attendue pour chaque question",
    ):
        calculer_score(reponses_incompletes)


def test_calcul_score_avec_toutes_les_bonnes_reponses():
    bonnes_reponses = [
        question.index_correct
        for question in QCM_MATHEMATIQUES
    ]

    score = calculer_score(bonnes_reponses)

    assert score == 10.0


def test_calcul_score_avec_toutes_les_mauvaises_reponses():
    mauvaises_reponses = [
        (question.index_correct + 1)
        % len(question.propositions)
        for question in QCM_MATHEMATIQUES
    ]

    score = calculer_score(mauvaises_reponses)

    assert score == 0.0