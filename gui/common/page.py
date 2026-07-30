# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Composants communs de mise en page et de navigation.

"""Éléments graphiques communs aux pages principales.

Un seul helper pour l'instant (``create_page_header``), mis dans son
propre fichier plutôt que dans ``messages.py`` parce qu'il s'agit de mise
en page (widgets), alors que ``messages.py`` s'occupe des appels API et
des erreurs — deux responsabilités qu'on a préféré séparer.
"""

from tkinter import ttk


def create_page_header(parent, title: str, back_command) -> ttk.Frame:
    """Construit l'en-tête standard des pages : titre à gauche, bouton « Retour au tableau de bord » à droite.

    Utilisé par tous les écrans principaux (élèves, questionnaires,
    sessions, statistiques, cours) pour garder une présentation cohérente.

    Paramètres :
        parent : widget parent dans lequel insérer l'en-tête.
        title : titre affiché pour la page.
        back_command : fonction appelée lors du clic sur « Retour au
            tableau de bord » (typiquement ``parent.show_dashboard``).

    Retour :
        Le cadre (``ttk.Frame``) contenant l'en-tête, déjà empaqueté.
    """
    header = ttk.Frame(parent)
    header.pack(fill="x", pady=(0, 12))

    ttk.Label(
        header,
        text=title,
        font=("Arial", 20, "bold"),
    ).pack(side="left")

    ttk.Button(
        header,
        text="Retour au tableau de bord",
        command=back_command,
    ).pack(side="right")

    return header
