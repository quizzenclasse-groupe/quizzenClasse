# database/tables_association.py
# *******************************************************
# Nom ......... : tables_association.py
# Rôle ........ : Déclare les tables d’association SQLAlchemy
#                 utilisées pour les relations plusieurs-à-
#                 plusieurs entre les enseignants, les
#                 établissements, les niveaux, les élèves,
#                 les équipes, les options et les cours.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/tables_association.py
# Usage ....... : Module chargé lors de l’import des modèles
#                 SQLAlchemy de l’application.
# *******************************************************
from sqlalchemy import Column, ForeignKey, Integer, Table

from database.base import Model


# Récupération de l'objet MetaData commun à tous les modèles ORM.
metadata = Model.metadata


# 1. Relation Enseignant <-> Etablissement
enseignant_etablissement = Table(
    "enseignant_etablissement",
    metadata,
    Column(
        "enseignant_id",
        Integer,
        ForeignKey("utilisateurs.id"),
        primary_key=True,
    ),
    Column(
        "etablissement_id",
        Integer,
        ForeignKey("etablissement.id"),
        primary_key=True,
    ),
)


# 2. Relation Enseignant <-> Niveau
enseignant_niveau = Table(
    "enseignant_niveau",
    metadata,
    Column(
        "enseignant_id",
        Integer,
        ForeignKey("utilisateurs.id"),
        primary_key=True,
    ),
    Column(
        "niveau_id",
        Integer,
        ForeignKey("niveau.id"),
        primary_key=True,
    ),
)


# 3. Relation Niveau <-> Eleve
niveau_eleve = Table(
    "niveau_eleve",
    metadata,
    Column(
        "niveau_id",
        Integer,
        ForeignKey("niveau.id"),
        primary_key=True,
    ),
    Column(
        "eleve_id",
        Integer,
        ForeignKey("participant.id"),
        primary_key=True,
    ),
)


# 4. Relation Eleve <-> Option
eleve_option = Table(
    "eleve_option",
    metadata,
    Column(
        "eleve_id",
        Integer,
        ForeignKey("participant.id"),
        primary_key=True,
    ),
    Column(
        "option_id",
        Integer,
        ForeignKey("option.id"),
        primary_key=True,
    ),
)


# 5. Relation Eleve <-> Equipe
equipe_eleve = Table(
    "equipe_eleve",
    metadata,
    Column(
        "eleve_id",
        Integer,
        ForeignKey("participant.id"),
        primary_key=True,
    ),
    Column(
        "equipe_id",
        Integer,
        ForeignKey("participant.id"),
        primary_key=True,
    ),
)


# 6. Relation Enseignant <-> Cours
enseignant_cours = Table(
    "enseignant_cours",
    metadata,
    Column(
        "enseignant_id",
        Integer,
        ForeignKey("utilisateurs.id"),
        primary_key=True,
    ),
    Column(
        "cours_id",
        Integer,
        ForeignKey("cours.id"),
        primary_key=True,
    ),
)


# 7. Relation Eleve <-> Cours
eleve_cours = Table(
    "eleve_cours",
    metadata,
    Column(
        "eleve_id",
        Integer,
        ForeignKey("participant.id"),
        primary_key=True,
    ),
    Column(
        "cours_id",
        Integer,
        ForeignKey("cours.id"),
        primary_key=True,
    ),
)