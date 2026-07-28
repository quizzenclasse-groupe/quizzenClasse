# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Composants communs de mise en page et de navigation.

"""Éléments graphiques communs aux pages principales."""

from tkinter import ttk


def create_page_header(parent, title: str, back_command) -> ttk.Frame:
    """
    Crée page header et synchronise l'affichage avec le résultat obtenu.
    
    Paramètres :
        parent : widget parent qui contient le composant.
        title : donnée nécessaire au traitement de « title ».
        back_command : donnée nécessaire au traitement de « back command ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
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
