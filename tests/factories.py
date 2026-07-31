# tests/factories.py
# *******************************************************
# Nom ......... : factories.py
# Rôle ........ : Regroupe les fabriques, jeux de données et
#                 fonctions utilitaires employés par les tests
#                 pour créer des établissements, niveaux,
#                 élèves, équipes, questionnaires, sessions et
#                 simulations de réponses.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile tests/factories.py
# Usage ....... : Importer les fabriques dans les fichiers de
#                 tests, par exemple :
#                 from tests.factories import creer_eleves
# ********************************************************
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import importlib
import random
from typing import Any, Sequence

from database.models.models_participants import Eleve, Equipe
from database.models.models_scolaire import Etablissement, Niveau


PRENOMS = [
    "Alice", "Benoît", "Chloé", "David", "Emma", "Farid", "Giulia",
    "Hugo", "Inès", "Jules", "Kenza", "Léo", "Maya", "Noah", "Olivia",
    "Paul", "Quentin", "Rania", "Sofia", "Thomas", "Ulysse", "Valentine",
    "William", "Xavier", "Yasmine", "Zoé", "Anaïs", "Baptiste", "Camille",
    "Dorian", "Élodie", "Florian", "Gaëlle", "Henri", "Ismaël", "Jade",
    "Karim", "Lina", "Maël", "Nina", "Oscar", "Perrine", "Romain",
    "Salomé", "Tiago", "Victoria", "Wassim", "Yanis", "Zélie", "Adrien",
    "Brune", "Célestin", "Diane", "Evan", "Fatou", "Gabin", "Héloïse",
    "Ilan", "Joséphine", "Kylian",
]

NOMS = [
    "Armand", "Bernard", "Carpentier", "Diallo", "Etienne", "Fontaine",
    "Giraud", "Henry", "Ibrahim", "Joseph", "Klein", "Laurent", "Moreau",
    "Nicolas", "Olivier", "Petit", "Quentin", "Robert", "Simon", "Thomas",
    "Urbain", "Vincent", "Wagner", "Xavier", "Yao", "Zamora", "André",
    "Benoit", "Césaire", "Dumont", "Elie", "Fabre", "Grondin", "Hoarau",
    "Imbert", "Jean", "Karam", "Lebon", "Martial", "Nadeau", "Orville",
    "Perrin", "Rivière", "Saint-Louis", "Tessier", "Valentin", "Wilfrid",
    "Yvon", "Zéphyr", "Auguste", "Baron", "Clément", "Desroses",
    "Eustache", "Féral", "Germain", "Hervé", "Isidor", "Jourdain",
    "Lacoste",
]


@dataclass(frozen=True)
class QuestionQCM:
    enonce: str
    propositions: tuple[str, str, str, str]
    index_correct: int


QCM_MATHEMATIQUES: tuple[QuestionQCM, ...] = (
    QuestionQCM("Combien vaut 7 × 8 ?", ("54", "56", "58", "64"), 1),
    QuestionQCM("Quelle est la racine carrée de 81 ?", ("7", "8", "9", "10"), 2),
    QuestionQCM("Quelle valeur approche le mieux π ?", ("2,72", "3,14", "1,62", "4,13"), 1),
    QuestionQCM("Lequel de ces nombres est premier ?", ("21", "29", "39", "51"), 1),
    QuestionQCM("Combien vaut 2 puissance 5 ?", ("10", "16", "25", "32"), 3),
    QuestionQCM("Somme des angles d'un triangle ?", ("90°", "180°", "270°", "360°"), 1),
    QuestionQCM("Dérivée de x² ?", ("x", "2x", "x²", "2"), 1),
    QuestionQCM("Valeur décimale de 1010 en binaire ?", ("8", "9", "10", "12"), 2),
    QuestionQCM("Écriture décimale de 1/4 ?", ("0,20", "0,25", "0,40", "0,75"), 1),
    QuestionQCM("Théorème de Pythagore ?", ("a+b=c", "a²+b²=c²", "a×b=c²", "a²-b²=c"), 1),
)


def creer_etablissement(
    *,
    code_uai: str,
    nom: str,
    academie: str,
    code_postal: str,
    adresse: str,
    departement: str,
    nom_departement: str,
) -> Etablissement:
    return Etablissement(
        code_uai=code_uai,
        nom_etablissement=nom,
        statut_public_prive="Public",
        adresse_1=adresse,
        adresse_2=None,
        adresse_3=None,
        code_postal=code_postal,
        code_departement=departement,
        nom_departement=nom_departement,
        nom_academie=academie,
        type_etablissement="etablissement",
    )


def etablissements_scenario() -> tuple[Etablissement, Etablissement]:
    return (
        creer_etablissement(
            code_uai="9720003W",
            nom="Lycée Victor Schoelcher",
            academie="Martinique",
            code_postal="97233",
            adresse="Schoelcher",
            departement="972",
            nom_departement="Martinique",
        ),
        creer_etablissement(
            code_uai="0690192J",
            nom="INSA Lyon",
            academie="Lyon",
            code_postal="69100",
            adresse="Villeurbanne",
            departement="069",
            nom_departement="Rhône",
        ),
    )


def creer_niveau(*, nom: str, etablissement: Etablissement, enseignant: Any) -> Niveau:
    return Niveau(
        nom_niveau=nom,
        effectif=0,
        etablissement=etablissement,
        enseignant=enseignant,
    )


def generer_identites(nombre: int, *, seed: int = 2026) -> list[tuple[str, str]]:
    if nombre > min(len(PRENOMS), len(NOMS)):
        raise ValueError("Nombre d'identités demandé trop élevé.")

    indices = list(range(min(len(PRENOMS), len(NOMS))))
    random.Random(seed).shuffle(indices)
    return [(NOMS[i], PRENOMS[i]) for i in indices[:nombre]]


def creer_eleves(
    niveau: Niveau,
    *,
    nombre: int = 30,
    seed: int = 2026,
    annee_naissance: int = 2009,
) -> list[Eleve]:
    eleves: list[Eleve] = []

    for numero, (nom, prenom) in enumerate(
        generer_identites(nombre, seed=seed),
        start=1,
    ):
        eleve = Eleve.creer(
            nom=nom,
            prenom=prenom,
            date_naissance=date(
                annee_naissance,
                ((numero - 1) % 12) + 1,
                ((numero - 1) % 28) + 1,
            ),
            redoublant=False,
            ville=niveau.etablissement.nom_etablissement,
            cp=niveau.etablissement.code_postal,
        )
        niveau.ajouterEleve(eleve)
        eleves.append(eleve)

    niveau.effectif = len(niveau.eleves)
    return eleves


def former_groupes_de_trois(
    eleves: Sequence[Eleve],
    *,
    prefixe: str,
) -> list[Equipe]:
    if len(eleves) % 3 != 0:
        raise ValueError("Le nombre d'élèves doit être divisible par trois.")

    return [
        Equipe.creer_depuis_eleves(
            nom=f"{prefixe}-{numero:02d}",
            eleves=list(eleves[debut:debut + 3]),
        )
        for numero, debut in enumerate(range(0, len(eleves), 3), start=1)
    ]


def simuler_reponses(*, numero_groupe: int, decalage: int = 0) -> list[int]:
    nombre_bonnes_reponses = max(1, 10 - numero_groupe)
    reponses: list[int] = []

    for index_question, question in enumerate(QCM_MATHEMATIQUES):
        if index_question < nombre_bonnes_reponses:
            reponses.append(question.index_correct)
        else:
            reponses.append(
                (question.index_correct + 1 + decalage) % len(question.propositions)
            )

    return reponses


def calculer_score(reponses: Sequence[int]) -> float:
    if len(reponses) != len(QCM_MATHEMATIQUES):
        raise ValueError("Une réponse est attendue pour chaque question.")

    return float(sum(
        reponse == question.index_correct
        for reponse, question in zip(reponses, QCM_MATHEMATIQUES)
    ))


def charger_classes_evaluation() -> dict[str, type]:
    module = importlib.import_module("database.models.models_evaluation")
    noms = (
        "Questionnaire",
        "Question",
        "Proposition",
        "SessionQuestionnaire",
        "RapportSession",
        "StatistiquesSession",
    )

    classes = {nom: getattr(module, nom, None) for nom in noms}
    manquantes = [nom for nom, classe in classes.items() if classe is None]

    if manquantes:
        raise AssertionError(
            "Classes absentes de models_evaluation.py : "
            + ", ".join(manquantes)
        )

    return classes  # type: ignore[return-value]


def creer_questionnaire_math(enseignant: Any) -> Any:
    classes = charger_classes_evaluation()
    Questionnaire = classes["Questionnaire"]
    Question = classes["Question"]
    Proposition = classes["Proposition"]

    questionnaire = Questionnaire(
        titre="QCM de culture générale mathématique",
        niveau="Première et première année post-bac",
        matiere="Mathématiques",
        difficulte="Basique",
        date_creation=date.today(),
        auteur=enseignant,
    )

    if not hasattr(questionnaire, "ajouterQuestion"):
        raise AssertionError("Questionnaire doit implémenter ajouterQuestion().")

    for donnee in QCM_MATHEMATIQUES:
        question = Question(enonce=donnee.enonce, type_question="QCM")

        if not hasattr(question, "ajouterProposition"):
            raise AssertionError("Question doit implémenter ajouterProposition().")

        for index, libelle in enumerate(donnee.propositions):
            try:
                proposition = Proposition(
                    libelle=libelle,
                    est_correcte=(index == donnee.index_correct),
                )
            except TypeError:
                proposition = Proposition(
                    texte=libelle,
                    est_correcte=(index == donnee.index_correct),
                )
            question.ajouterProposition(proposition)

        questionnaire.ajouterQuestion(question)

    return questionnaire


def creer_session_questionnaire(*, questionnaire: Any, titre: str) -> Any:
    classes = charger_classes_evaluation()
    SessionQuestionnaire = classes["SessionQuestionnaire"]

    if hasattr(SessionQuestionnaire, "creer"):
        return SessionQuestionnaire.creer(
            questionnaire=questionnaire,
            titre=titre,
            mode="groupe",
        )

    objet = SessionQuestionnaire(
        nom_session=titre,
        date_debut=None,
        date_fin=None,
    )
    if hasattr(objet, "questionnaire"):
        objet.questionnaire = questionnaire
    return objet
