# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Fonctions de validation et de normalisation des données saisies.

"""
Fonctions de validation utilisées par l'interface QuizzenClasse.

Version : GUI V1.1

Les validations sont placées dans un fichier séparé afin de :

    - réduire la taille des fenêtres graphiques ;
    - réutiliser les mêmes règles dans plusieurs modules ;
    - faciliter les tests ;
    - permettre à un autre développeur de modifier les règles sans toucher
      à la construction graphique.
"""

from __future__ import annotations

from datetime import date, datetime
import re


def clean_text(value: str) -> str:
    # Enlève les espaces en trop, y compris ceux au milieu du texte.
    return " ".join(value.strip().split())


def is_required(value: str) -> bool:
    return bool(clean_text(value))


def validate_date(
    value: str,
    date_format: str = "%d/%m/%Y",
) -> tuple[bool, str]:
    """Vérifie qu'une date de naissance est présente, au bon format, et pas dans le futur."""
    cleaned_value = clean_text(value)

    if not cleaned_value:
        return False, "La date de naissance est obligatoire."

    try:
        parsed_date = datetime.strptime(
            cleaned_value,
            date_format,
        ).date()
    except ValueError:
        return (
            False,
            "La date doit respecter le format JJ/MM/AAAA.",
        )

    if parsed_date > date.today():
        return (
            False,
            "La date de naissance ne peut pas être dans le futur.",
        )

    return True, ""


def validate_postal_code(value: str) -> tuple[bool, str]:
    # Un code postal français = 5 chiffres, rien d'autre.
    cleaned_value = clean_text(value)

    if not cleaned_value:
        return False, "Le code postal est obligatoire."

    if not re.fullmatch(r"\d{5}", cleaned_value):
        return (
            False,
            "Le code postal doit contenir exactement cinq chiffres.",
        )

    return True, ""


def validate_person_name(
    value: str,
    field_name: str,
) -> tuple[bool, str]:
    """Vérifie qu'un nom/prénom n'est pas vide, fait au moins 2 caractères et ne contient que des lettres, espaces, tirets ou apostrophes."""
    cleaned_value = clean_text(value)

    if not cleaned_value:
        return False, f"Le champ « {field_name} » est obligatoire."

    if len(cleaned_value) < 2:
        return (
            False,
            f"Le champ « {field_name} » doit contenir au moins deux caractères.",
        )

    allowed_pattern = r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+"

    if not re.fullmatch(allowed_pattern, cleaned_value):
        return (
            False,
            f"Le champ « {field_name} » contient des caractères non autorisés.",
        )

    return True, ""


def validate_required_text(
    value: str,
    field_name: str,
) -> tuple[bool, str]:
    if not is_required(value):
        return False, f"Le champ « {field_name} » est obligatoire."

    return True, ""
