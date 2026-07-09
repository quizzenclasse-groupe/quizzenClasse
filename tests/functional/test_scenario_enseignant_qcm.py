from __future__ import annotations

import pytest

from database.models.models_participants import Participation
from database.services.connexion_service import ConnexionService
from tests.factories import (
    calculer_score,
    charger_classes_evaluation,
    creer_eleves,
    creer_niveau,
    creer_questionnaire_math,
    creer_session_questionnaire,
    etablissements_scenario,
    former_groupes_de_trois,
    simuler_reponses,
)


pytestmark = [
    pytest.mark.integration,
    pytest.mark.contract,
]


def test_scenario_complet_enseignant_qcm_groupes_rapports(session):
    """
    Vérifie la collaboration de l'authentification, du parcours scolaire,
    des groupes, du QCM, des sessions, des participations et des rapports.
    """
    classes = charger_classes_evaluation()
    StatistiquesSession = classes["StatistiquesSession"]
    RapportSession = classes["RapportSession"]

    # Inscription et authentification.
    connexion = ConnexionService(session)
    enseignant_inscrit = connexion.inscrireEnseignant(
        "dominique.scenario",
        "MotDePasse-2026",
    )
    connexion.deconnecter()

    enseignant = connexion.connecter(
        "dominique.scenario",
        "MotDePasse-2026",
    )

    assert enseignant is not None
    assert enseignant.id == enseignant_inscrit.id

    # Établissements et niveaux.
    lycee_schoelcher, insa_lyon = etablissements_scenario()
    niveau_premiere = creer_niveau(
        nom="Première S",
        etablissement=lycee_schoelcher,
        enseignant=enseignant,
    )
    niveau_prepa = creer_niveau(
        nom="Première année de prépa",
        etablissement=insa_lyon,
        enseignant=enseignant,
    )

    # Trente élèves par niveau.
    eleves_premiere = creer_eleves(
        niveau_premiere,
        nombre=30,
        seed=2026,
        annee_naissance=2009,
    )
    eleves_prepa = creer_eleves(
        niveau_prepa,
        nombre=30,
        seed=2027,
        annee_naissance=2007,
    )

    # Dix groupes de trois par niveau.
    groupes_premiere = former_groupes_de_trois(
        eleves_premiere,
        prefixe="PREMIERE-S",
    )
    groupes_prepa = former_groupes_de_trois(
        eleves_prepa,
        prefixe="PREPA-INSA",
    )

    # Questionnaire et sessions.
    questionnaire = creer_questionnaire_math(enseignant)
    session_premiere = creer_session_questionnaire(
        questionnaire=questionnaire,
        titre="Session Première S",
    )
    session_prepa = creer_session_questionnaire(
        questionnaire=questionnaire,
        titre="Session Prépa INSA",
    )

    session.add_all([
        lycee_schoelcher,
        insa_lyon,
        niveau_premiere,
        niveau_prepa,
        *eleves_premiere,
        *eleves_prepa,
        *groupes_premiere,
        *groupes_prepa,
        questionnaire,
        session_premiere,
        session_prepa,
    ])
    session.flush()

    session_premiere.lancer()
    session_prepa.lancer()

    # Réponses et scores déterministes.
    participations_premiere: list[Participation] = []
    participations_prepa: list[Participation] = []

    for numero, groupe in enumerate(groupes_premiere):
        score = calculer_score(
            simuler_reponses(numero_groupe=numero)
        )
        participation = Participation(
            session_questionnaire_id=session_premiere.id,
            participant_id=groupe.id,
        )
        participation.evaluer(
            score=score,
            commentaire_final=f"Score déterministe : {score}/10",
        )
        participations_premiere.append(participation)

    for numero, groupe in enumerate(groupes_prepa):
        score = calculer_score(
            simuler_reponses(
                numero_groupe=numero,
                decalage=1,
            )
        )
        participation = Participation(
            session_questionnaire_id=session_prepa.id,
            participant_id=groupe.id,
        )
        participation.evaluer(
            score=score,
            commentaire_final=f"Score déterministe : {score}/10",
        )
        participations_prepa.append(participation)

    session.add_all(
        participations_premiere + participations_prepa
    )
    session.flush()

    session_premiere.clore()
    session_prepa.clore()

    statistiques_premiere = (
        StatistiquesSession.genererRapportSession(
            participations_premiere
        )
    )
    statistiques_prepa = (
        StatistiquesSession.genererRapportSession(
            participations_prepa
        )
    )

    rapport_premiere = RapportSession.generer(
        statistiques_premiere
    )
    rapport_prepa = RapportSession.generer(
        statistiques_prepa
    )

    session.commit()

    assert len(niveau_premiere.eleves) == 30
    assert len(niveau_prepa.eleves) == 30
    assert len(groupes_premiere) == 10
    assert len(groupes_prepa) == 10
    assert all(len(groupe.membres) == 3 for groupe in groupes_premiere)
    assert all(len(groupe.membres) == 3 for groupe in groupes_prepa)
    assert len(questionnaire.questions) == 10
    assert len(participations_premiere) == 10
    assert len(participations_prepa) == 10

    scores_attendus = [
        10.0, 9.0, 8.0, 7.0, 6.0,
        5.0, 4.0, 3.0, 2.0, 1.0,
    ]
    assert [p.score for p in participations_premiere] == scores_attendus
    assert [p.score for p in participations_prepa] == scores_attendus

    assert session_premiere.date_debut is not None
    assert session_premiere.date_fin is not None
    assert session_prepa.date_debut is not None
    assert session_prepa.date_fin is not None
    assert rapport_premiere is not None
    assert rapport_prepa is not None
