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
    """
    Représente eleves window dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
        """
        Effectue le traitement correspondant à create header dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))
        ttk.Label(header, text="Gestion des niveaux et des élèves", font=("Arial", 20, "bold")).pack(side="left")
        ttk.Button(header, text="Retour au tableau de bord", command=self.parent.show_dashboard).pack(side="right")

    def _create_content(self) -> None:
        """
        Effectue le traitement correspondant à create content dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        main_content = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_content.pack(fill="both", expand=True)
        self.niveau_section = NiveauSection(main_content, self.api, self._handle_niveau_selected)
        self.eleve_section = EleveSection(main_content, self.api, self._handle_student_niveau_changed)
        main_content.add(self.niveau_section, weight=1)
        main_content.add(self.eleve_section, weight=2)

    def _handle_niveau_selected(self, niveau_id) -> None:
        """
        Effectue le traitement correspondant à handle niveau selected dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.eleve_section.set_current_niveau(niveau_id)

    def _handle_student_niveau_changed(self, niveau_id: int) -> None:
        """
        Effectue le traitement correspondant à handle student niveau changed dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.niveau_section.refresh(niveau_id)
        self.eleve_section.set_current_niveau(niveau_id)
