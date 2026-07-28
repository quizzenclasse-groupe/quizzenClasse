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
    """
    Effectue le traitement correspondant à clean text dans le contexte de cette fenêtre.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

    return " ".join(value.strip().split())


def is_required(value: str) -> bool:
    """
    Effectue le traitement correspondant à is required dans le contexte de cette fenêtre.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

    return bool(clean_text(value))


def validate_date(
    value: str,
    date_format: str = "%d/%m/%Y",
) -> tuple[bool, str]:
    """
    Valide date et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
        date_format : donnée nécessaire au traitement de « date format ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

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
    """
    Valide postal code et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

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
    """
    Valide person name et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
        field_name : donnée nécessaire au traitement de « field name ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

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
    """
    Valide required text et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        value : donnée nécessaire au traitement de « value ».
        field_name : donnée nécessaire au traitement de « field name ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

    if not is_required(value):
        return False, f"Le champ « {field_name} » est obligatoire."

    return True, ""
