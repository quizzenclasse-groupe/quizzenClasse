# api/repositories/base.py
# Rôle : Repository générique qui regroupe les opérations CRUD élémentaires
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin

"""
Repository générique : encapsule les opérations CRUD élémentaires
communes à (presque) toutes les entités SQLAlchemy du projet.

Rôle de la couche "repository" dans l'architecture Router -> Service ->
Repository -> Modèle (reprise du pattern déjà utilisé sur Quiz_app) :
  - c'est la seule couche qui parle directement à SQLAlchemy
    (Session.add/commit/execute...) ;
  - elle ne contient aucune règle métier ni contrôle de droits
    (c'est le rôle de la couche service, juste au-dessus) ;
  - elle peut être testée ou remplacée indépendamment du reste
    (par exemple pour brancher un autre moteur de stockage).

Chaque repository spécifique (NiveauRepository, EleveRepository, ...)
hérite de `BaseRepository` et ajoute les requêtes propres à son entité
(recherches filtrées, jointures, etc.).
"""

from __future__ import annotations

from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from database.base import Model

ModelType = TypeVar("ModelType", bound=Model)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: OrmSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    def obtenir(self, id_: int) -> ModelType | None:
        """Récupère une ligne par sa clé primaire, ou None si absente."""
        return self.session.get(self.model, id_)

    def lister(self) -> list[ModelType]:
        """Récupère toutes les lignes de la table (à utiliser avec parcimonie)."""
        return list(self.session.execute(select(self.model)).scalars().all())

    def ajouter(self, instance: ModelType) -> ModelType:
        """
        Ajoute une nouvelle instance et effectue immédiatement le commit.

        On commit systématiquement ici (plutôt que de laisser la
        transaction ouverte) car chaque requête HTTP correspond à une
        session de courte durée (cf. `api/deps.py::get_db`) : il n'y a
        pas de notion d'unité de travail répartie sur plusieurs requêtes.
        """
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def sauvegarder(self, instance: ModelType) -> ModelType:
        """
        Persiste les modifications faites sur une instance déjà suivie
        par la session (SQLAlchemy détecte automatiquement les
        changements d'attributs : pas besoin de rappeler `session.add`).
        """
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def supprimer(self, instance: ModelType) -> None:
        self.session.delete(instance)
        self.session.commit()
