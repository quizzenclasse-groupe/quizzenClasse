# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion des questionnaires, questions et propositions de réponse.

"""Page complète de création, consultation et suppression des QCM."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from gui.common.messages import run_api_action
from gui.common.page import create_page_header
from .question_form import QuestionForm
from .questions_table import QuestionsTable


class QuestionnairesWindow(ttk.Frame):
    """
    Représente questionnaires window dans l'interface graphique QuizzenClasse.
    
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
        # Toute la page est défilable. Les tableaux gardent également leurs
        # propres barres de défilement pour les longues listes.
        """
        Effectue le traitement correspondant à create content dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
            """
            Met à jour scroll region et synchronise l'affichage avec le résultat obtenu.
            
            Paramètres :
                _event : donnée nécessaire au traitement de « event ».
            
            Retour :
                Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
            
            Traitement :
                Les contrôles de saisie et les erreurs attendues sont pris en compte avant
                d'actualiser les widgets concernés ou de poursuivre la navigation.
            """
            canvas.configure(scrollregion=canvas.bbox("all"))

        def fit_inner_width(event) -> None:
            """
            Effectue le traitement correspondant à fit inner width dans le contexte de cette fenêtre.
            
            Paramètres :
                event : événement Tkinter à l’origine de l’appel.
            
            Retour :
                Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
            
            Traitement :
                Les contrôles de saisie et les erreurs attendues sont pris en compte avant
                d'actualiser les widgets concernés ou de poursuivre la navigation.
            """
            canvas.itemconfigure(inner_window, width=event.width)

        def on_mousewheel(event) -> None:
            # Windows/macOS utilisent event.delta ; Linux utilise aussi
            # Button-4 et Button-5, gérés ci-dessous.
            """
            Traite l’événement lié à mousewheel et synchronise l'affichage avec le résultat obtenu.
            
            Paramètres :
                event : événement Tkinter à l’origine de l’appel.
            
            Retour :
                Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
            
            Traitement :
                Les contrôles de saisie et les erreurs attendues sont pris en compte avant
                d'actualiser les widgets concernés ou de poursuivre la navigation.
            """
            if event.delta:
                canvas.yview_scroll(int(-event.delta / 120), "units")

        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        inner.bind("<Configure>", update_scroll_region)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        canvas.bind("<Configure>", fit_inner_width)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        canvas.bind_all("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"))
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
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
        """
        Effectue le traitement correspondant à create metadata form dans le contexte de cette fenêtre.
        
        Paramètres :
            parent : widget parent qui contient le composant.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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
        """
        Effectue le traitement correspondant à create actions dans le contexte de cette fenêtre.
        
        Paramètres :
            parent : widget parent qui contient le composant.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Enregistrer", command=self.save).pack(side="left", padx=3)
        ttk.Button(actions, text="Nouveau", command=self.clear).pack(side="left", padx=3)
        ttk.Button(actions, text="Supprimer", command=self.delete_selected).pack(side="left", padx=3)

    def _create_questionnaire_list(self, parent) -> None:
        """
        Effectue le traitement correspondant à create questionnaire list dans le contexte de cette fenêtre.
        
        Paramètres :
            parent : widget parent qui contient le composant.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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

        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.list_tree.bind("<<TreeviewSelect>>", self.load_selected)
        ttk.Button(
            frame, text="Actualiser", command=self.refresh_questionnaires
        ).pack(pady=6)

    def add_question(self, question: dict) -> None:
        """
        Ajoute question et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            question : donnée nécessaire au traitement de « question ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.selected_id is None:
            self.questions.append(question)
            self.questions_table.refresh(self.questions)
            return

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(
            lambda: self.api.add_question(self.selected_id, question)
        )
        if result is not None:
            self.questions = result.get("questions", [])
            self.questions_table.refresh(self.questions)

    def _has_sessions(self) -> bool | None:
        """
        Effectue le traitement correspondant à has sessions dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.selected_id is None:
            return False
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        sessions = run_api_action(lambda: self.api.list_sessions(self.selected_id))
        if sessions is None:
            return None
        return bool(sessions)

    def add_proposition(self, index: int) -> None:
        """
        Ajoute proposition et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            index : donnée nécessaire au traitement de « index ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
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
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        est_correcte = messagebox.askyesno("Bonne réponse", "Cette proposition est-elle correcte ?", parent=self)
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
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
        """
        Supprime question et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            index : donnée nécessaire au traitement de « index ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(
            lambda: self.api.delete_question(self.selected_id, question["id"])
        )
        if result is not None:
            self.questions = result.get("questions", [])
            self.questions_table.refresh(self.questions)

    def save(self) -> None:
        """
        Effectue le traitement correspondant à save dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        title = self.titre_var.get().strip()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not title:
            messagebox.showwarning("Titre obligatoire", "Saisissez un titre.")
            return

        metadata = {
            "titre": title,
            "niveau": self.niveau_var.get().strip() or None,
            "matiere": self.matiere_var.get().strip() or None,
            "difficulte": self.difficulte_var.get() or None,
        }

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        if self.selected_id is None:
            metadata["questions"] = self.questions
            result = run_api_action(lambda: self.api.create_questionnaire(metadata))
        else:
            # L'API autorise ici uniquement la modification des métadonnées.
            result = run_api_action(
                lambda: self.api.update_questionnaire(self.selected_id, metadata)
            )

        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if result is not None:
            messagebox.showinfo("Enregistrement", "Questionnaire enregistré.")
            self.clear()
            self.refresh_questionnaires()

    def refresh_questionnaires(self) -> None:
        """
        Actualise questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        questionnaires = run_api_action(self.api.list_questionnaires)
        if questionnaires is None:
            return
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.list_tree.delete(*self.list_tree.get_children())
        # Met à jour le contenu du tableau affiché dans l'interface.
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
        """
        Charge selected et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.list_tree.selection()
        if not selection:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
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
        """
        Supprime selected et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un questionnaire.")
            return
        has_sessions = self._has_sessions()
        if has_sessions is None:
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if has_sessions:
            messagebox.showwarning(
                "Questionnaire déjà utilisé",
                "Ce questionnaire possède déjà une ou plusieurs sessions et ne peut pas être supprimé depuis la GUI.",
            )
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not messagebox.askyesno("Confirmation", "Supprimer ce questionnaire non utilisé ?"):
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.delete_questionnaire(self.selected_id))
        if result:
            self.clear()
            self.refresh_questionnaires()

    def clear(self) -> None:
        """
        Effectue le traitement correspondant à clear dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.selected_id = None
        self.titre_var.set("")
        self.niveau_var.set("")
        self.matiere_var.set("")
        self.difficulte_var.set("Moyen")
        self.questions.clear()
        self.questions_table.refresh(self.questions)
        self.list_tree.selection_remove(self.list_tree.selection())
