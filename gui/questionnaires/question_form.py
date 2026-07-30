# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Formulaire de saisie d'une question et de ses réponses.

"""Formulaire réutilisable pour construire une question QCM.

Utilisé uniquement par ``QuestionnairesWindow`` : une fois une question
validée ici, elle est transmise telle quelle (voir ``on_add``) et affichée
dans ``QuestionsTable``, à côté. Ce formulaire ne sait rien de l'API ni
du reste du questionnaire.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class QuestionForm(ttk.LabelFrame):
    """Formulaire de saisie d'une question à choix multiples (énoncé + 4 propositions au plus).

    Ne communique jamais directement avec l'API : à la validation, elle
    transmet simplement la question construite à ``on_add``, fourni par
    l'écran parent (``QuestionnairesWindow.add_question``).
    """

    def __init__(self, parent, on_add) -> None:
        """Construit les champs du formulaire.

        Paramètres :
            parent : widget parent qui contient ce formulaire.
            on_add : fonction appelée avec le dictionnaire de la question
                validée (énoncé, type, propositions) à chaque soumission réussie.
        """
        super().__init__(parent, text="Nouvelle question", padding=10)
        self.on_add = on_add
        self.enonce_var = tk.StringVar()
        self.proposition_vars = [tk.StringVar() for _ in range(4)]
        self.correct_vars = [tk.BooleanVar() for _ in range(4)]
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Construit le champ énoncé, les 4 lignes de proposition et leur case « Correcte »."""
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
        """Valide le formulaire (énoncé non vide, au moins 2 propositions, au moins une correcte) puis appelle ``on_add``.

        Les propositions laissées vides sont ignorées silencieusement,
        seules celles avec un texte saisi sont transmises.
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

        if not enonce:
            messagebox.showwarning("Question incomplète", "Saisissez un énoncé.")
            return
        if len(propositions) < 2:
            messagebox.showwarning(
                "Question incomplète",
                "Saisissez au moins deux propositions.",
            )
            return
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
        """Vide l'énoncé et les 4 propositions, décoche les cases « Correcte »."""
        self.enonce_var.set("")
        for text_var, correct_var in zip(self.proposition_vars, self.correct_vars):
            text_var.set("")
            correct_var.set(False)
