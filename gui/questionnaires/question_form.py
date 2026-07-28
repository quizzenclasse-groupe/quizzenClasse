# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Formulaire de saisie d'une question et de ses réponses.

"""Formulaire réutilisable pour construire une question QCM."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class QuestionForm(ttk.LabelFrame):
    """
    Représente question form dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self, parent, on_add) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            on_add : donnée nécessaire au traitement de « on add ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent, text="Nouvelle question", padding=10)
        self.on_add = on_add
        self.enonce_var = tk.StringVar()
        self.proposition_vars = [tk.StringVar() for _ in range(4)]
        self.correct_vars = [tk.BooleanVar() for _ in range(4)]
        self._create_widgets()

    def _create_widgets(self) -> None:
        """
        Effectue le traitement correspondant à create widgets dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        ttk.Label(self, text="Énoncé :").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.enonce_var).grid(
            row=0, column=1, columnspan=2, sticky="ew", pady=4
        )

        for index in range(4):
            ttk.Label(self, text=f"Proposition {index + 1} :").grid(
                row=index + 1, column=0, sticky="w", pady=3
            )
            ttk.Entry(self, textvariable=self.proposition_vars[index]).grid(
                row=index + 1, column=1, sticky="ew", pady=3
            )
            ttk.Checkbutton(
                self,
                text="Correcte",
                variable=self.correct_vars[index],
            ).grid(row=index + 1, column=2, padx=5)

        ttk.Button(self, text="Ajouter la question", command=self._submit).grid(
            row=5, column=0, columnspan=3, pady=(8, 0)
        )
        self.columnconfigure(1, weight=1)

    def _submit(self) -> None:
        """
        Effectue le traitement correspondant à submit dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        enonce = self.enonce_var.get().strip()
        propositions = []

        for text_var, correct_var in zip(self.proposition_vars, self.correct_vars):
            libelle = text_var.get().strip()
            if libelle:
                propositions.append({
                    "libelle": libelle,
                    "est_correcte": correct_var.get(),
                })

        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not enonce:
            messagebox.showwarning("Question incomplète", "Saisissez un énoncé.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if len(propositions) < 2:
            messagebox.showwarning(
                "Question incomplète",
                "Saisissez au moins deux propositions.",
            )
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not any(item["est_correcte"] for item in propositions):
            messagebox.showwarning(
                "Bonne réponse absente",
                "Cochez au moins une proposition correcte.",
            )
            return

        self.on_add({
            "enonce": enonce,
            "type_question": "QCM",
            "propositions": propositions,
        })
        self.clear()

    def clear(self) -> None:
        """
        Effectue le traitement correspondant à clear dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.enonce_var.set("")
        for text_var, correct_var in zip(self.proposition_vars, self.correct_vars):
            text_var.set("")
            correct_var.set(False)
