# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion des questionnaires, questions et propositions de réponse.

"""Page complète de création, consultation et suppression des QCM.

L'écran est coupé en 3 parties qui se partagent le travail :
``QuestionForm`` (formulaire pour saisir une question + ses propositions),
``QuestionsTable`` (tableau récapitulatif des questions déjà ajoutées),
et cette classe ``QuestionnairesWindow`` qui les fait fonctionner
ensemble et gère les métadonnées (titre, niveau, matière, difficulté)
ainsi que la liste des questionnaires déjà enregistrés à droite.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from gui.common.messages import run_api_action
from gui.common.page import create_page_header
from .question_form import QuestionForm
from .questions_table import QuestionsTable


class QuestionnairesWindow(ttk.Frame):
    """Écran de gestion des questionnaires : métadonnées, questions/propositions, et liste des QCM existants.

    Deux modes de fonctionnement pour les questions : tant que le
    questionnaire n'est pas encore enregistré (``selected_id is None``),
    les questions sont gérées uniquement en mémoire locale ; une fois
    enregistré, chaque ajout/suppression de question passe par l'API.
    """

    def __init__(self, parent) -> None:
        """Initialise l'état de l'écran, construit le contenu, puis charge la liste des questionnaires.

        Paramètres :
            parent : fenêtre principale de l'application (fournit
                ``api_client`` et ``show_dashboard`` pour le bouton retour).
        """
        super().__init__(parent, padding=18)
        self.parent = parent
        self.api = parent.api_client
        self.questions: list[dict] = []
        self.selected_id: int | None = None

        self.titre_var = tk.StringVar()
        self.niveau_var = tk.StringVar()
        self.matiere_var = tk.StringVar()
        self.difficulte_var = tk.StringVar(value="Moyen")

        self.pack(fill="both", expand=True)
        create_page_header(self, "Gestion des questionnaires", parent.show_dashboard)
        self._create_content()
        self.refresh_questionnaires()

    def _create_content(self) -> None:
        """Construit la page défilable : éditeur de questionnaire à gauche, liste des QCM à droite.

        Toute la page est défilable (canvas + scrollbar globale) ; les
        tableaux internes gardent en plus leurs propres barres de
        défilement pour les longues listes de questions ou de questionnaires.
        """
        scroll_area = ttk.Frame(self)
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_area, highlightthickness=0)
        page_scrollbar = ttk.Scrollbar(
            scroll_area, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=page_scrollbar.set)

        page_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = ttk.Frame(canvas)
        inner_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def update_scroll_region(_event=None) -> None:
            """Recalcule la zone défilable d'après la taille réelle du contenu."""
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_inner_width(event) -> None:
            """Aligne la largeur du cadre interne sur celle du canvas parent."""
            canvas.itemconfigure(inner_window, width=event.width)

        def on_mousewheel(event) -> None:
            """Fait défiler la page à la molette (Windows/macOS ; Linux via Button-4/5 ci-dessous)."""
            if event.delta:
                canvas.yview_scroll(int(-event.delta / 120), "units")

        inner.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", fit_inner_width)
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda _e: canvas.yview_scroll(1, "units"))

        content = ttk.Frame(inner)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)

        editor = ttk.Frame(content, padding=5)
        listing = ttk.Frame(content, padding=5)
        editor.grid(row=0, column=0, sticky="nsew")
        listing.grid(row=0, column=1, sticky="nsew")

        self._create_metadata_form(editor)

        QuestionForm(editor, self.add_question).pack(fill="x", pady=(10, 0))

        self._create_actions(editor)

        self.questions_table = QuestionsTable(
            editor,
            self.delete_question,
            self.add_proposition,
        )
        self.questions_table.pack(fill="both", expand=True, pady=(2, 0))

        self._create_questionnaire_list(listing)

    def _create_metadata_form(self, parent) -> None:
        """Construit le formulaire des métadonnées du questionnaire (titre, niveau, matière, difficulté)."""
        form = ttk.LabelFrame(parent, text="Informations générales", padding=10)
        form.pack(fill="x")
        fields = (
            ("Titre * :", self.titre_var),
            ("Niveau :", self.niveau_var),
            ("Matière :", self.matiere_var),
        )
        for row, (label, variable) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=variable).grid(
                row=row, column=1, sticky="ew", padx=5, pady=3
            )

        ttk.Label(form, text="Difficulté :").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.difficulte_var,
            values=("Facile", "Moyen", "Difficile"),
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", padx=5, pady=3)
        form.columnconfigure(1, weight=1)

    def _create_actions(self, parent) -> None:
        """Construit la barre de boutons Enregistrer / Nouveau / Supprimer de l'éditeur."""
        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Enregistrer", command=self.save).pack(side="left", padx=3)
        ttk.Button(actions, text="Nouveau", command=self.clear).pack(side="left", padx=3)
        ttk.Button(actions, text="Supprimer", command=self.delete_selected).pack(side="left", padx=3)

    def _create_questionnaire_list(self, parent) -> None:
        """Construit le tableau listant les questionnaires existants de l'enseignant."""
        frame = ttk.LabelFrame(parent, text="Mes questionnaires", padding=8)
        frame.pack(fill="both", expand=True)

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.list_tree = ttk.Treeview(
            table_frame,
            columns=("titre", "matiere", "difficulte", "questions"),
            show="headings",
        )
        for name, title, width in (
            ("titre", "Titre", 180),
            ("matiere", "Matière", 100),
            ("difficulte", "Difficulté", 90),
            ("questions", "Questions", 90),
        ):
            self.list_tree.heading(name, text=title)
            self.list_tree.column(
                name, width=width, minwidth=width, stretch=(name == "titre"),
            )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.list_tree.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.list_tree.xview
        )
        self.list_tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.list_tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.list_tree.bind("<<TreeviewSelect>>", self.load_selected)
        ttk.Button(
            frame, text="Actualiser", command=self.refresh_questionnaires
        ).pack(pady=6)

    def add_question(self, question: dict) -> None:
        """Ajoute une question au questionnaire en cours d'édition.

        Avant le premier enregistrement, la question est simplement ajoutée
        à la liste locale ``self.questions`` ; une fois le questionnaire
        enregistré (``selected_id`` connu), l'ajout passe par l'API pour
        recevoir en retour la question avec son identifiant définitif.
        """
        if self.selected_id is None:
            self.questions.append(question)
            self.questions_table.refresh(self.questions)
            return

        result = run_api_action(
            lambda: self.api.add_question(self.selected_id, question)
        )
        if result is not None:
            self.questions = result.get("questions", [])
            self.questions_table.refresh(self.questions)

    def _has_sessions(self) -> bool | None:
        """Indique si le questionnaire sélectionné a déjà au moins une session créée.

        Sert de garde-fou avant suppression : un questionnaire déjà utilisé
        dans une session ne doit pas être supprimable depuis la GUI.
        """
        if self.selected_id is None:
            return False
        sessions = run_api_action(lambda: self.api.list_sessions(self.selected_id))
        if sessions is None:
            return None
        return bool(sessions)

    def add_proposition(self, index: int) -> None:
        """Demande le texte d'une nouvelle proposition et l'ajoute à la question désignée par ``index``.

        Nécessite que le questionnaire soit déjà enregistré (une question
        sans identifiant API ne peut pas recevoir de proposition côté serveur).
        """
        if self.selected_id is None:
            messagebox.showinfo(
                "Questionnaire non enregistré",
                "Enregistrez d'abord le questionnaire. Les réponses des nouvelles questions se saisissent dans le formulaire au-dessus.",
            )
            return
        question = self.questions[index]
        question_id = question.get("id")
        if question_id is None:
            return
        libelle = simpledialog.askstring("Nouvelle réponse", "Texte de la proposition :", parent=self)
        if not libelle or not libelle.strip():
            return
        est_correcte = messagebox.askyesno("Bonne réponse", "Cette proposition est-elle correcte ?", parent=self)
        result = run_api_action(
            lambda: self.api.add_proposition(
                self.selected_id, question_id,
                {"libelle": libelle.strip(), "est_correcte": est_correcte},
            )
        )
        if result is not None:
            self.questions[index] = result
            self.questions_table.refresh(self.questions)

    def delete_question(self, index: int) -> None:
        """Supprime la question à l'index donné, localement si le questionnaire n'est pas encore enregistré, sinon via l'API."""
        question = self.questions[index]
        if self.selected_id is None or "id" not in question:
            self.questions.pop(index)
            self.questions_table.refresh(self.questions)
            return

        # La GUI suit directement la route DELETE prévue par l'API.
        # Si le backend refuse la suppression à cause de données liées,
        # l'erreur réelle sera affichée par run_api_action.
        if not messagebox.askyesno("Confirmation", "Supprimer cette question du questionnaire ?"):
            return
        result = run_api_action(
            lambda: self.api.delete_question(self.selected_id, question["id"])
        )
        if result is not None:
            self.questions = result.get("questions", [])
            self.questions_table.refresh(self.questions)

    def save(self) -> None:
        """Crée le questionnaire (avec ses questions) s'il n'est pas encore enregistré, sinon met à jour ses métadonnées."""
        title = self.titre_var.get().strip()
        if not title:
            messagebox.showwarning("Titre obligatoire", "Saisissez un titre.")
            return

        metadata = {
            "titre": title,
            "niveau": self.niveau_var.get().strip() or None,
            "matiere": self.matiere_var.get().strip() or None,
            "difficulte": self.difficulte_var.get() or None,
        }

        if self.selected_id is None:
            metadata["questions"] = self.questions
            result = run_api_action(lambda: self.api.create_questionnaire(metadata))
        else:
            # L'API autorise ici uniquement la modification des métadonnées.
            result = run_api_action(
                lambda: self.api.update_questionnaire(self.selected_id, metadata)
            )

        if result is not None:
            messagebox.showinfo("Enregistrement", "Questionnaire enregistré.")
            self.clear()
            self.refresh_questionnaires()

    def refresh_questionnaires(self) -> None:
        """Recharge la liste des questionnaires de l'enseignant et repeuple le tableau."""
        questionnaires = run_api_action(self.api.list_questionnaires)
        if questionnaires is None:
            return
        self.list_tree.delete(*self.list_tree.get_children())
        for item in questionnaires:
            self.list_tree.insert(
                "",
                "end",
                iid=str(item["id"]),
                values=(
                    item["titre"],
                    item.get("matiere") or "",
                    item.get("difficulte") or "",
                    item.get("nombre_questions", 0),
                ),
            )

    def load_selected(self, _event=None) -> None:
        """Charge le questionnaire sélectionné dans le tableau (métadonnées et questions) pour édition."""
        selection = self.list_tree.selection()
        if not selection:
            return
        questionnaire = run_api_action(
            lambda: self.api.get_questionnaire(int(selection[0]))
        )
        if questionnaire is None:
            return
        self.selected_id = questionnaire["id"]
        self.titre_var.set(questionnaire["titre"])
        self.niveau_var.set(questionnaire.get("niveau") or "")
        self.matiere_var.set(questionnaire.get("matiere") or "")
        self.difficulte_var.set(questionnaire.get("difficulte") or "Moyen")
        self.questions = questionnaire.get("questions", [])
        self.questions_table.refresh(self.questions)

    def delete_selected(self) -> None:
        """Supprime le questionnaire sélectionné, à condition qu'il n'ait encore aucune session."""
        if self.selected_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un questionnaire.")
            return
        has_sessions = self._has_sessions()
        if has_sessions is None:
            return
        if has_sessions:
            messagebox.showwarning(
                "Questionnaire déjà utilisé",
                "Ce questionnaire possède déjà une ou plusieurs sessions et ne peut pas être supprimé depuis la GUI.",
            )
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce questionnaire non utilisé ?"):
            return
        result = run_api_action(lambda: self.api.delete_questionnaire(self.selected_id))
        if result:
            self.clear()
            self.refresh_questionnaires()

    def clear(self) -> None:
        """Réinitialise le formulaire d'édition (nouveau questionnaire vierge)."""
        self.selected_id = None
        self.titre_var.set("")
        self.niveau_var.set("")
        self.matiere_var.set("")
        self.difficulte_var.set("Moyen")
        self.questions.clear()
        self.questions_table.refresh(self.questions)
        self.list_tree.selection_remove(self.list_tree.selection())
