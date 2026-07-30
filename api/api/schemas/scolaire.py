# api/schemas/scolaire.py
# Rôle : Schémas Pydantic  pour tout ce qui touche au parcours scolaire (comme établissements, niveaux, élèves, équipes). 
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin


from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# Établissements

class EtablissementPublic(BaseModel):
    """Représentation d'un établissement scolaire (import CSV, cf. README)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_etablissement: str
    statut_public_prive: str
    code_uai: str | None = None
    nom_academie: str | None = None
    code_postal: str | None = None
    code_departement: str
    nom_departement: str



# Niveaux scolaires

class NiveauCreation(BaseModel):
    """Corps de requête pour créer un niveau (ex : "Terminale S")."""

    nom_niveau: str = Field(min_length=1, max_length=120)
    etablissement_id: int


class NiveauMiseAJour(BaseModel):
    """Corps de requête pour renommer un niveau existant."""

    nom_niveau: str = Field(min_length=1, max_length=120)


class NiveauPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_niveau: str
    effectif: int
    etablissement_id: int
    enseignant_id: int

    @classmethod
    def depuis_orm(cls, niveau) -> "NiveauPublic":
        """
        Le champ `effectif` du modèle `Niveau` est une colonne stockée,
        jamais mise à jour automatiquement lors de l'ajout d'un élève
        (aucune méthode du modèle d'origine ne le fait). Plutôt que
        d'exposer une valeur potentiellement fausse, on la recalcule ici
        à partir du nombre réel d'élèves rattachés (`niveau.eleves`).
        """
        return cls(
            id=niveau.id,
            nom_niveau=niveau.nom_niveau,
            effectif=len(niveau.eleves),
            etablissement_id=niveau.etablissement_id,
            enseignant_id=niveau.enseignant_id,
        )



# Élèves

class EleveCreation(BaseModel):
    """Corps de requête pour ajouter un élève à un (ou plusieurs) niveaux."""

    nom: str = Field(min_length=1, max_length=120)
    prenom: str = Field(min_length=1, max_length=120)
    date_naissance: date | None = None
    redoublant: bool = False
    ville: str | None = None
    cp: str | None = None
    niveau_ids: list[int] = Field(
        default_factory=list,
        description="Identifiants des niveaux auxquels rattacher l'élève.",
    )


class EleveMiseAJour(BaseModel):
    """
    Corps de requête pour modifier un élève.

    Tous les champs sont optionnels : seuls les champs transmis (non
    `None`) sont appliqués, exactement comme le fait déjà
    `Eleve.mettre_a_jour(**modifications)` côté modèle.
    """

    nom: str | None = None
    prenom: str | None = None
    date_naissance: date | None = None
    redoublant: bool | None = None
    ville: str | None = None
    cp: str | None = None


class EleveEnBref(BaseModel):
    """Vue allégée d'un élève, utilisée dans les listes imbriquées (équipes, participations)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_eleve: str | None = None
    prenom: str | None = None


class ElevePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_eleve: str | None = None
    prenom: str | None = None
    date_naissance: date | None = None
    redoublant: bool | None = None
    ville: str | None = None
    cp: str | None = None
    niveau_ids: list[int] = Field(default_factory=list)

    @classmethod
    def depuis_orm(cls, eleve) -> "ElevePublic":
        """
        Construction manuelle (plutôt que `model_validate` direct) car
        `niveau_ids` doit être dérivé de la relation `niveaux`
        (liste d'objets `Niveau`) et non lu tel quel sur le modèle.
        """
        return cls(
            id=eleve.id,
            nom_eleve=eleve.nom_eleve,
            prenom=eleve.prenom,
            date_naissance=eleve.date_naissance,
            redoublant=eleve.redoublant,
            ville=eleve.ville,
            cp=eleve.cp,
            niveau_ids=[niveau.id for niveau in eleve.niveaux],
        )



# Équipes (Groupes d^élèves)

class EquipeCreation(BaseModel):
    """Corps de requête pour créer une équipe à partir d'élèves existants."""

    nom_equipe: str = Field(min_length=1, max_length=120)
    eleve_ids: list[int] = Field(min_length=1)
    cours_id: int | None = None


class EquipePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_equipe: str | None = None
    cours_id: int | None = None
    membres: list[EleveEnBref] = Field(default_factory=list)
