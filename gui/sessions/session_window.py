# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Fenêtre principale du module sessions (création et suivi).

"""Création, animation et suivi des sessions de quiz.

Cette interface ne calcule aucune note : elle utilise les routes de l'API
pour créer une session à partir d'un questionnaire, l'ouvrir aux
participants, puis rediriger vers le lecteur de quiz (``SessionPlayerWindow``)
ou l'écran de participations (``ParticipationWindow``) selon l'action
choisie par l'enseignant.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from gui.common.messages import run_api_action
from gui.common.page import create_page_header
from gui.sessions.participation_window import ParticipationWindow
from gui.sessions.session_player import SessionPlayerWindow


class SessionWindow(ttk.Frame):
    """Écran de création des sessions et de suivi de leur cycle de vie (créée → en cours → clôturée)."""

    def __init__(self, parent) -> None:
        """Initialise l'état de la fenêtre, construit le formulaire et le tableau, puis charge les questionnaires.

        Paramètres :
            parent : fenêtre principale de l'application (fournit
                ``api_client`` et ``show_dashboard`` pour le bouton retour).
        """
        super().__init__(parent, padding=18)
        self.parent = parent
        self.api = parent.api_client
        self.questionnaire_ids: dict[str, int] = {}
        self.selected_session_id: int | None = None
        self.sessions_by_id: dict[int, dict] = {}

        self.name_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="individuel")
        self.questionnaire_var = tk.StringVar()
        self.share_code_var = tk.StringVar(value="Code de partage : —")

        self.pack(fill="both", expand=True)
        create_page_header(self, "Sessions de quiz", parent.show_dashboard)
        self._create_form()
        self._create_table()
        self.load_questionnaires()

    def _create_form(self) -> None:
        """Construit le formulaire de création : nom, questionnaire source et mode (individuel/équipe)."""
        form = ttk.LabelFrame(self, text="Nouvelle session", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Nom de la session :").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(form, text="Questionnaire :").grid(row=1, column=0, sticky="w")
        self.questionnaire_combo = ttk.Combobox(form, textvariable=self.questionnaire_var, state="readonly")
        self.questionnaire_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        # Changer de questionnaire recharge la liste des sessions déjà créées pour celui-ci.
        self.questionnaire_combo.bind("<<ComboboxSelected>>", self.load_sessions)

        ttk.Label(form, text="Mode :").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form, textvariable=self.mode_var, values=("individuel", "equipe"), state="readonly").grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Button(form, text="Créer la session", command=self.create_session).grid(
            row=3, column=0, columnspan=2, pady=(8, 0)
        )
        form.columnconfigure(1, weight=1)

    def _create_table(self) -> None:
        """Construit le tableau des sessions du questionnaire sélectionné et sa barre d'actions."""
        frame = ttk.LabelFrame(self, text="Sessions du questionnaire", padding=8)
        frame.pack(fill="both", expand=True, pady=(12, 0))

        tree_container = ttk.Frame(frame)
        tree_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("nom", "mode", "debut", "fin", "statut"),
            show="headings",
            selectmode="browse",
        )
        for name, title, width in (
            ("nom", "Nom", 260),
            ("mode", "Mode", 90),
            ("debut", "Début", 110),
            ("fin", "Fin", 110),
            ("statut", "Statut", 100),
        ):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width)
        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)
        # Retient la session sélectionnée pour les boutons d'action ci-dessous.
        self.tree.bind("<<TreeviewSelect>>", self._remember_selection)
        # Double-clic sur une ligne : raccourci pour lancer directement l'animation.
        self.tree.bind("<Double-1>", lambda _event: self.animate_session())

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(7, 0))
        ttk.Button(actions, text="Démarrer", command=self.start_session).pack(side="left", padx=3)
        ttk.Button(actions, text="Animer la session", command=self.animate_session).pack(side="left", padx=3)
        ttk.Button(actions, text="Participations / notes", command=self.manage_participations).pack(side="left", padx=3)
        ttk.Button(actions, text="Clôturer", command=self.close_session).pack(side="left", padx=3)
        ttk.Button(actions, text="Afficher le code", command=self.show_share_code).pack(side="left", padx=3)
        ttk.Label(actions, textvariable=self.share_code_var).pack(side="right", padx=5)

    def load_questionnaires(self) -> None:
        """Charge la liste des questionnaires de l'enseignant et sélectionne le premier par défaut."""
        items = run_api_action(self.api.list_questionnaires)
        if items is None:
            return
        self.questionnaire_ids = {item["titre"]: item["id"] for item in items}
        self.questionnaire_combo["values"] = list(self.questionnaire_ids)
        if items:
            self.questionnaire_var.set(items[0]["titre"])
            self.load_sessions()

    def _current_questionnaire_id(self) -> int | None:
        """Renvoie l'identifiant du questionnaire actuellement sélectionné dans le formulaire."""
        return self.questionnaire_ids.get(self.questionnaire_var.get())

    def create_session(self) -> None:
        """Valide le formulaire puis crée une session pour le questionnaire choisi."""
        questionnaire_id = self._current_questionnaire_id()
        name = self.name_var.get().strip()
        if not questionnaire_id or not name:
            messagebox.showwarning("Données incomplètes", "Choisissez un questionnaire et saisissez un nom de session.")
            return
        result = run_api_action(lambda: self.api.create_session({
            "nom_session": name,
            "mode": self.mode_var.get(),
            "questionnaire_id": questionnaire_id,
        }))
        if result is not None:
            self.name_var.set("")
            self.load_sessions()
            messagebox.showinfo("Session créée", "La session a été créée.")

    def load_sessions(self, _event=None) -> None:
        """Recharge les sessions du questionnaire sélectionné et repeuple le tableau."""
        questionnaire_id = self._current_questionnaire_id()
        if questionnaire_id is None:
            return
        sessions = run_api_action(lambda: self.api.list_sessions(questionnaire_id))
        if sessions is None:
            return
        self.sessions_by_id = {item["id"]: item for item in sessions}
        self.selected_session_id = None
        self.share_code_var.set("Code de partage : —")
        self.tree.delete(*self.tree.get_children())
        for item in sessions:
            self.tree.insert("", "end", iid=str(item["id"]), values=(
                item["nom_session"], item["mode"], item.get("date_debut") or "—",
                item.get("date_fin") or "—", item["statut"],
            ))

    def _remember_selection(self, _event=None) -> None:
        """Mémorise l'identifiant de la session sélectionnée dans le tableau."""
        selection = self.tree.selection()
        self.selected_session_id = int(selection[0]) if selection else None

    def _require_session(self) -> int | None:
        """Renvoie la session sélectionnée, ou avertit l'enseignant et renvoie ``None`` si aucune ne l'est."""
        if self.selected_session_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez une session.")
        return self.selected_session_id

    def _load_participations_required(self, session_id: int) -> list[dict] | None:
        """Charge les participations de la session et avertit si aucune n'existe encore.

        Utilisé avant de démarrer ou d'animer une session : sans participant
        inscrit, ni l'un ni l'autre n'a de sens.
        """
        participations = run_api_action(lambda: self.api.list_participations(session_id))
        if participations is None:
            return None
        if not participations:
            messagebox.showwarning(
                "Aucun participant",
                "Inscrivez au moins un participant avant de démarrer ou d'animer la session.",
            )
            return None
        return participations

    def start_session(self) -> None:
        """Passe la session sélectionnée à l'état « en cours », après vérification qu'elle a des participants."""
        session_id = self._require_session()
        if not session_id or self._load_participations_required(session_id) is None:
            return
        current = self.sessions_by_id.get(session_id, {})
        if current.get("statut") == "cloturee":
            messagebox.showwarning("Session clôturée", "Cette session est déjà clôturée.")
            return
        if current.get("statut") == "en_cours":
            messagebox.showinfo("Session", "Cette session est déjà démarrée.")
            return
        if run_api_action(lambda: self.api.start_session(session_id)) is not None:
            self.load_sessions()
            if self.tree.exists(str(session_id)):
                self.tree.selection_set(str(session_id))
                self.selected_session_id = session_id
            messagebox.showinfo("Session", "La session est maintenant ouverte aux réponses.")

    def animate_session(self) -> None:
        """Ouvre le lecteur de quiz (``SessionPlayerWindow``) pour la session sélectionnée.

        Démarre la session si nécessaire (avec confirmation), récupère le
        code de partage puis la session publique, et n'ouvre le lecteur que
        s'il reste des participants n'ayant pas encore de score.
        """
        session_id = self._require_session()
        if not session_id or self._load_participations_required(session_id) is None:
            return

        current = self.sessions_by_id.get(session_id, {})
        if current.get("statut") == "cloturee":
            messagebox.showwarning("Session clôturée", "Une session clôturée ne peut plus recevoir de réponses.")
            return
        if current.get("statut") != "en_cours":
            if not messagebox.askyesno(
                "Démarrer la session",
                "La session doit être démarrée avant la correction automatique. La démarrer maintenant ?",
            ):
                return
            if run_api_action(lambda: self.api.start_session(session_id)) is None:
                return
            self.load_sessions()
            self.selected_session_id = session_id

        code_payload = run_api_action(lambda: self.api.get_share_code(session_id))
        if not code_payload:
            return
        code = code_payload["code"]
        self.share_code_var.set(f"Code de partage : {code}")

        public_session = run_api_action(lambda: self.api.open_public_session(session_id, code))
        if public_session is None:
            return
        if not public_session.get("participants_en_attente"):
            messagebox.showinfo(
                "Aucune réponse en attente",
                "Tous les participants inscrits ont déjà obtenu un score.",
            )
            return
        SessionPlayerWindow(self, public_session, session_id, code, current.get("mode", "individuel"))

    def close_session(self) -> None:
        """Clôture définitivement la session sélectionnée (elle ne pourra plus recevoir de réponses)."""
        session_id = self._require_session()
        if session_id and run_api_action(lambda: self.api.close_session(session_id)) is not None:
            self.load_sessions()

    def show_share_code(self) -> None:
        """Affiche (ou récupère si besoin) le code de partage de la session sélectionnée."""
        session_id = self._require_session()
        if not session_id:
            return
        result = run_api_action(lambda: self.api.get_share_code(session_id))
        if result:
            self.share_code_var.set(f"Code de partage : {result['code']}")

    def manage_participations(self) -> None:
        """Ouvre la fenêtre de gestion des participations pour la session sélectionnée."""
        session_id = self._require_session()
        if session_id:
            ParticipationWindow(self, self.api, session_id, self.sessions_by_id.get(session_id, {}).get("mode", "individuel"))
