import pytest

from database.models.models_participants import Eleve, Equipe


def creer_eleve(nom: str) -> Eleve:
    return Eleve.creer(
        nom=nom,
        prenom="Test",
        date_naissance=None,
        redoublant=False,
    )


def test_creation_equipe_avec_trois_eleves():
    eleves = [
        creer_eleve("Martin"),
        creer_eleve("Durand"),
        creer_eleve("Bernard"),
    ]

    equipe = Equipe.creer_depuis_eleves(
        nom="Groupe 1",
        eleves=eleves,
    )

    assert equipe.nom_equipe == "Groupe 1"
    assert len(equipe.membres) == 3
    assert equipe.membres == eleves


def test_creation_groupe_refuse_une_liste_vide():
    with pytest.raises(ValueError):
        Equipe.creer_depuis_eleves(
            nom="Groupe vide",
            eleves=[],
        )


def test_creation_groupe_refuse_un_nom_vide():
    eleve = creer_eleve("Martin")

    with pytest.raises(ValueError):
        Equipe.creer_depuis_eleves(
            nom="",
            eleves=[eleve],
        )