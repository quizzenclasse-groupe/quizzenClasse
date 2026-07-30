# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Page principale de gestion des niveaux et des élèves.

"""Fenêtre coordinatrice de la gestion des niveaux et des élèves."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .eleve_section import EleveSection
from .niveau_section import NiveauSection


class ElevesWindow(ttk.Frame):
    """Écran de gestion des niveaux et des élèves : deux panneaux côte à côte, redimensionnables.

    À gauche ``NiveauSection`` (liste des niveaux de l'enseignant), à
    droite ``EleveSection`` (élèves du niveau sélectionné). Cette classe
    ne fait aucun appel API elle-même : c'est un pur coordinateur qui
    relie les deux sections par deux callbacks croisés — sélectionner un
    niveau à gauche recharge les élèves à droite, et ajouter/modifier un
    élève à droite met à jour l'effectif affiché à gauche. Toute la
    logique métier (formulaires, validation, appels API) vit dans les
    deux sections elles-mêmes.
    """

    def __init__(self, parent) -> None:
        """Construit l'en-tête et les deux sections, puis charge les données initiales.

        Paramètres :
            parent : fenêtre principale de l'application (fournit
                ``api_client`` et ``show_dashboard`` pour le bouton retour).
        """
        super().__init__(parent, padding=15)
        self.parent = parent
        self.api = parent.api_client
        self.pack(fill="both", expand=True)
        self._create_header()
        self._create_content()
        self.niveau_section.refresh()
        self.eleve_section.refresh_niveaux()

    def _create_header(self) -> None:
        """Construit le titre de la page et le bouton de retour au tableau de bord."""
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))
        ttk.Label(header, text="Gestion des niveaux et des élèves", font=("Arial", 20, "bold")).pack(side="left")
        ttk.Button(header, text="Retour au tableau de bord", command=self.parent.show_dashboard).pack(side="right")

    def _create_content(self) -> None:
        """Place ``NiveauSection`` et ``EleveSection`` dans un ``Panedwindow`` horizontal redimensionnable."""
        main_content = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_content.pack(fill="both", expand=True)
        self.niveau_section = NiveauSection(main_content, self.api, self._handle_niveau_selected)
        self.eleve_section = EleveSection(main_content, self.api, self._handle_student_niveau_changed)
        main_content.add(self.niveau_section, weight=1)
        main_content.add(self.eleve_section, weight=2)

    def _handle_niveau_selected(self, niveau_id) -> None:
        """Relaie le changement de niveau sélectionné vers ``EleveSection``."""
        self.eleve_section.set_current_niveau(niveau_id)

    def _handle_student_niveau_changed(self, niveau_id: int) -> None:
        """Rafraîchit le tableau des niveaux (effectif) après l'ajout ou la modification d'un élève."""
        self.niveau_section.refresh(niveau_id)
        self.eleve_section.set_current_niveau(niveau_id)
