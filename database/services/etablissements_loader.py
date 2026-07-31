# database/services/etablissements_loader.py
# *******************************************************
# Nom ......... : etablissements_loader.py
# Rôle ........ : Lit le fichier CSV de référence des
#                 établissements scolaires, nettoie les
#                 valeurs, détecte les doublons selon le code
#                 UAI et prépare leur insertion ou mise à jour.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/services/etablissements_loader.py
# Usage ....... : Importer la fonction de chargement :
#                 load_etablissements_from_csv(
#                     session,
#                     chemin_csv,
#                 )
# *******************************************************
from __future__ import annotations

import csv
from pathlib import Path
from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.models_scolaire import Etablissement


def nettoyer(
    ligne: dict[str, str | None],
    cle: str,
    valeur_par_defaut: str | None = None,
) -> str | None:
    """
    Récupère une valeur du CSV et supprime les espaces inutiles.
    """
    valeur = ligne.get(cle)

    if valeur is None:
        return valeur_par_defaut

    valeur = valeur.strip()

    return valeur if valeur else valeur_par_defaut


def load_etablissements_from_csv(
    s: Session,
    csv_path: Union[str, Path],
    *,
    dedupe: bool = True,
    update_on_duplicate: bool = False,
) -> int:
    """
    Lit le fichier CSV des établissements et ajoute les données à la session.

    La fonction ne réalise pas de commit.

    La déduplication repose sur le code UAI de l'établissement.

    Retourne le nombre d'insertions ou de mises à jour effectuées.
    """
    csv_path = Path(csv_path)
    modifications = 0

    etablissements_par_uai: dict[str, Etablissement] = {}

    if dedupe:
        etablissements_existants = s.scalars(
            select(Etablissement)
        ).all()

        etablissements_par_uai = {
            etablissement.code_uai: etablissement
            for etablissement in etablissements_existants
            if etablissement.code_uai
        }

    with csv_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as fichier:
        reader = csv.DictReader(
            fichier,
            delimiter=";",
        )

        for row in reader:
            code_uai = nettoyer(
                row,
                "Identifiant_de_l_etablissement",
            )

            nom = nettoyer(
                row,
                "Nom_etablissement",
            )

            # Une ligne sans code UAI ou sans nom n'est pas exploitable.
            if not code_uai or not nom:
                continue

            existe = (
                etablissements_par_uai.get(code_uai)
                if dedupe
                else None
            )

            if existe is not None:
                if update_on_duplicate:
                    existe.nom_etablissement = nom
                    existe.statut_public_prive = nettoyer(
                        row,
                        "Statut_public_prive",
                        "Inconnu",
                    )
                    existe.adresse_1 = nettoyer(
                        row,
                        "Adresse_1",
                        "",
                    )
                    existe.adresse_2 = nettoyer(
                        row,
                        "Adresse_2",
                    )
                    existe.adresse_3 = nettoyer(
                        row,
                        "Adresse_3",
                    )
                    existe.code_postal = nettoyer(
                        row,
                        "Code_postal",
                    )
                    existe.code_departement = nettoyer(
                        row,
                        "Code_departement",
                        "00",
                    )
                    existe.nom_departement = nettoyer(
                        row,
                        "Libelle_departement",
                        "Inconnu",
                    )
                    existe.nom_academie = nettoyer(
                        row,
                        "Libelle_academie",
                    )

                    modifications += 1

                continue

            etablissement = Etablissement(
                code_uai=code_uai,
                nom_etablissement=nom,
                statut_public_prive=nettoyer(
                    row,
                    "Statut_public_prive",
                    "Inconnu",
                ),
                adresse_1=nettoyer(
                    row,
                    "Adresse_1",
                    "",
                ),
                adresse_2=nettoyer(
                    row,
                    "Adresse_2",
                ),
                adresse_3=nettoyer(
                    row,
                    "Adresse_3",
                ),
                code_postal=nettoyer(
                    row,
                    "Code_postal",
                ),
                code_departement=nettoyer(
                    row,
                    "Code_departement",
                    "00",
                ),
                nom_departement=nettoyer(
                    row,
                    "Libelle_departement",
                    "Inconnu",
                ),
                nom_academie=nettoyer(
                    row,
                    "Libelle_academie",
                ),

                # Discriminateur ORM de la classe Etablissement.
                type_etablissement="etablissement",
            )

            s.add(etablissement)

            if dedupe:
                etablissements_par_uai[code_uai] = etablissement

            modifications += 1

            if modifications % 1000 == 0:
                s.flush()

    return modifications
