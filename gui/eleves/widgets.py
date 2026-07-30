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
    """Ajoute une ligne « libellé + champ de saisie » sur une grille ``grid()``, et renvoie le champ créé.

    Paramètres :
        parent : conteneur dans lequel la ligne est ajoutée (doit utiliser ``grid``).
        label_text : texte du libellé affiché à gauche du champ.
        variable : ``StringVar``/``IntVar`` liée au champ de saisie.
        row : numéro de ligne de la grille où placer le libellé et le champ.
        width : largeur du champ de saisie en caractères.

    Retour :
        Le widget ``ttk.Entry`` créé, si l'appelant a besoin d'y accéder
        directement (focus, liaison d'événement, etc.).
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
