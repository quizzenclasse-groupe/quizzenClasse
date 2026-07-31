# tests/integration/test_groupes_persistence.py
# *******************************************************
# Nom ......... : test_groupes_persistence.py
# Rôle ........ : Vérifie la persistance des équipes d'élèves,
#                 leur rechargement depuis la base de données
#                 et la répartition correcte des élèves entre
#                 les différentes équipes.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 tests/integration/test_groupes_persistence.py
# Usage ....... : Pour exécuter ce fichier de tests :
#                 python -m pytest \
#                 tests/integration/test_groupes_persistence.py -q
# *******************************************************
from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.models_participants import Equipe
from database.services.connexion_service import ConnexionService
from tests.factories import (
    creer_eleves,
    creer_niveau,
    etablissements_scenario,
    former_groupes_de_trois,
)


pytestmark = pytest.mark.integration


def test_trente_eleves_forment_dix_groupes_persistes(session):
    # Arrange : création de l’enseignant.
    service = ConnexionService(session)

    enseignant = service.inscrireEnseignant(
        "enseignant.groupes.persistes",
        "MotDePasse-2026",
    )

    # Création de l’établissement et du niveau scolaire.
    lycee_schoelcher, _ = etablissements_scenario()

    niveau = creer_niveau(
        nom="Première S",
        etablissement=lycee_schoelcher,
        enseignant=enseignant,
    )

    # Création déterministe de trente élèves.
    eleves = creer_eleves(
        niveau,
        nombre=30,
        seed=2026,
        annee_naissance=2009,
    )

    session.add_all(
        [
            lycee_schoelcher,
            niveau,
            *eleves,
        ]
    )
    session.flush()

    # Act : constitution de dix groupes de trois élèves.
    groupes = former_groupes_de_trois(
        eleves,
        prefixe="PREMIERE-S",
    )

    session.add_all(groupes)
    session.commit()

    ids_groupes = [groupe.id for groupe in groupes]
    ids_eleves = {eleve.id for eleve in eleves}

    # Suppression des objets du cache de la session afin de forcer
    # leur rechargement depuis la base de données.
    session.expunge_all()

    groupes_recharges = session.scalars(
        select(Equipe)
        .options(selectinload(Equipe.membres))
        .where(Equipe.id.in_(ids_groupes))
        .order_by(Equipe.id)
    ).all()

    # Assert : les dix groupes ont bien été persistés.
    assert len(groupes_recharges) == 10

    # Chaque groupe contient exactement trois élèves.
    assert all(
        len(groupe.membres) == 3
        for groupe in groupes_recharges
    )

    # Les noms des groupes ont été correctement enregistrés.
    assert {
        groupe.nom_equipe
        for groupe in groupes_recharges
    } == {
        f"PREMIERE-S-{numero:02d}"
        for numero in range(1, 11)
    }

    # Les trente élèves sont répartis une seule fois dans les groupes.
    ids_membres = [
        eleve.id
        for groupe in groupes_recharges
        for eleve in groupe.membres
    ]

    assert len(ids_membres) == 30
    assert len(set(ids_membres)) == 30
    assert set(ids_membres) == ids_eleves

    # Aucun élève ne figure dans deux groupes différents.
    assert sum(
        len(groupe.membres)
        for groupe in groupes_recharges
    ) == 30