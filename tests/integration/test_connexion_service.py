from __future__ import annotations

import pytest

from database.models.models_utilisateurs import Enseignant
from database.services.connexion_service import ConnexionService


pytestmark = pytest.mark.unit


def test_inscription_cree_un_enseignant_actif(session):
    service = ConnexionService(session)

    enseignant = service.inscrireEnseignant(
        "dominique.test",
        "MotDePasse-2026",
    )

    assert enseignant.id is not None
    assert isinstance(enseignant, Enseignant)
    assert enseignant.nom_utilisateur == "dominique.test"
    assert enseignant.actif is True
    assert enseignant.type_utilisateur == "enseignant"
    assert enseignant.mdp_hash != "MotDePasse-2026"


def test_connexion_reussit_avec_les_bons_identifiants(session):
    service = ConnexionService(session)
    inscrit = service.inscrireEnseignant(
        "dominique.test",
        "MotDePasse-2026",
    )
    service.deconnecter()

    connecte = service.connecter(
        "dominique.test",
        "MotDePasse-2026",
    )

    assert connecte is not None
    assert connecte.id == inscrit.id
    assert service.utilisateurCourant is connecte


def test_connexion_refuse_un_mauvais_mot_de_passe(session):
    service = ConnexionService(session)
    service.inscrireEnseignant(
        "dominique.test",
        "MotDePasse-2026",
    )

    connecte = service.connecter(
        "dominique.test",
        "mot-de-passe-incorrect",
    )

    assert connecte is None
    assert service.utilisateurCourant is None


def test_inscription_refuse_un_nom_deja_utilise(session):
    service = ConnexionService(session)
    service.inscrireEnseignant(
        "dominique.test",
        "MotDePasse-2026",
    )

    with pytest.raises(ValueError, match="déjà utilisé"):
        service.inscrireEnseignant(
            "dominique.test",
            "AutreMotDePasse-2026",
        )
