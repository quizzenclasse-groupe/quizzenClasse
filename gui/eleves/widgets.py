# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Composants graphiques réutilisables pour la gestion scolaire.

"""Petits composants graphiques réutilisables du module élèves."""

from __future__ import annotations

from tkinter import ttk
from tkinter import Variable


def create_labeled_entry(
    parent,
    label_text: str,
    variable: Variable,
    row: int,
    *,
    width: int = 30,
) -> ttk.Entry:
    """
    Crée labeled entry et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        parent : widget parent qui contient le composant.
        label_text : donnée nécessaire au traitement de « label text ».
        variable : donnée nécessaire au traitement de « variable ».
        row : donnée nécessaire au traitement de « row ».
        width : donnée nécessaire au traitement de « width ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

    ttk.Label(
        parent,
        text=label_text,
    ).grid(
        row=row,
        column=0,
        padx=5,
        pady=5,
        sticky="w",
    )

    entry = ttk.Entry(
        parent,
        textvariable=variable,
        width=width,
    )
    entry.grid(
        row=row,
        column=1,
        padx=5,
        pady=5,
        sticky="ew",
    )

    parent.columnconfigure(1, weight=1)

    return entry
