from __future__ import annotations

import pytest

from database.services.connexion_service import ConnexionService
from tests.factories import (
    creer_eleves,
    creer_niveau,
    etablissements_scenario,
)


pytestmark = pytest.mark.unit


def test_creation_de_deux_niveaux_rattaches_aux_bons_etablissements(session):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.parcours",
        "MotDePasse-2026",
    )

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

    session.add_all([
        lycee_schoelcher,
        insa_lyon,
        niveau_premiere,
        niveau_prepa,
    ])
    session.commit()

    assert niveau_premiere.etablissement is lycee_schoelcher
    assert niveau_prepa.etablissement is insa_lyon
    assert niveau_premiere.enseignant is enseignant
    assert niveau_prepa.enseignant is enseignant


def test_trente_eleves_sont_inscrits_dans_chaque_niveau(session):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.eleves",
        "MotDePasse-2026",
    )

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

    session.add_all([
        lycee_schoelcher,
        insa_lyon,
        niveau_premiere,
        niveau_prepa,
        *eleves_premiere,
        *eleves_prepa,
    ])
    session.commit()

    assert len(niveau_premiere.eleves) == 30
    assert len(niveau_prepa.eleves) == 30

    assert niveau_premiere.effectif == 30
    assert niveau_prepa.effectif == 30

    tous_les_eleves = eleves_premiere + eleves_prepa

    assert len(tous_les_eleves) == 60
    assert len({eleve.id for eleve in tous_les_eleves}) == 60

    ids_premiere = {
        eleve.id
        for eleve in eleves_premiere
    }

    ids_prepa = {
        eleve.id
        for eleve in eleves_prepa
    }

    assert len(ids_premiere) == 30
    assert len(ids_prepa) == 30
    assert ids_premiere.isdisjoint(ids_prepa)


def test_un_eleve_est_rattache_au_niveau_qui_le_contient(session):
    service = ConnexionService(session)
    enseignant = service.inscrireEnseignant(
        "enseignant.relation",
        "MotDePasse-2026",
    )

    lycee_schoelcher, _ = etablissements_scenario()
    niveau = creer_niveau(
        nom="Première S",
        etablissement=lycee_schoelcher,
        enseignant=enseignant,
    )
    eleve = creer_eleves(niveau, nombre=1, seed=2030)[0]

    session.add_all([lycee_schoelcher, niveau, eleve])
    session.commit()

    assert eleve in niveau.eleves
    assert niveau in eleve.niveaux
