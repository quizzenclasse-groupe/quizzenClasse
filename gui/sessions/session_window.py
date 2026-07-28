# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Création, animation et suivi des sessions et participations.

"""Création, animation et suivi des sessions de quiz.

Cette interface ne calcule aucune note : elle utilise les routes de l'API
pour inscrire les participants, ouvrir la session publique et soumettre les
réponses à la correction automatique du backend.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from textwrap import wrap

from gui.common.messages import run_api_action
from gui.common.page import create_page_header


class VerticalScrolledFrame(ttk.Frame):
    """
    Représente vertical scrolled frame dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self, parent, **kwargs) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            **kwargs : donnée nécessaire au traitement de « kwargs ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.content.bind("<Configure>", self._update_scrollregion)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind("<Configure>", self._resize_content)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _update_scrollregion(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à update scrollregion dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event) -> None:
        """
        Effectue le traitement correspondant à resize content dans le contexte de cette fenêtre.
        
        Paramètres :
            event : événement Tkinter à l’origine de l’appel.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à bind mousewheel dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à unbind mousewheel dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.unbind_all("<MouseWheel>")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.unbind_all("<Button-4>")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event) -> None:
        """
        Effectue le traitement correspondant à on mousewheel dans le contexte de cette fenêtre.
        
        Paramètres :
            event : événement Tkinter à l’origine de l’appel.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_mousewheel_linux(self, event):
        """
        Fait défiler le contenu avec la molette sous Linux.

        Le contrôle d'existence évite d'utiliser le canvas lorsque la fenêtre
        qui le contient vient d'être fermée.
        """
        try:
             if self.canvas.winfo_exists():
                 self.canvas.yview_scroll(
                     -1 if event.num == 4 else 1,
                     "units"
                 )
        except tk.TclError:
           # La fenêtre peut être détruite entre le contrôle et le défilement.
           return
        


class SessionWindow(ttk.Frame):
    """
    Représente session window dans l'interface graphique QuizzenClasse.
    
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
        """
        Effectue le traitement correspondant à create form dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        form = ttk.LabelFrame(self, text="Nouvelle session", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Nom de la session :").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(form, text="Questionnaire :").grid(row=1, column=0, sticky="w")
        self.questionnaire_combo = ttk.Combobox(form, textvariable=self.questionnaire_var, state="readonly")
        self.questionnaire_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
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
        """
        Effectue le traitement correspondant à create table dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.tree.bind("<<TreeviewSelect>>", self._remember_selection)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
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
        """
        Charge questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        items = run_api_action(self.api.list_questionnaires)
        if items is None:
            return
        self.questionnaire_ids = {item["titre"]: item["id"] for item in items}
        self.questionnaire_combo["values"] = list(self.questionnaire_ids)
        if items:
            self.questionnaire_var.set(items[0]["titre"])
            self.load_sessions()

    def _current_questionnaire_id(self) -> int | None:
        """
        Effectue le traitement correspondant à current questionnaire id dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return self.questionnaire_ids.get(self.questionnaire_var.get())

    def create_session(self) -> None:
        """
        Crée session et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        questionnaire_id = self._current_questionnaire_id()
        name = self.name_var.get().strip()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not questionnaire_id or not name:
            messagebox.showwarning("Données incomplètes", "Choisissez un questionnaire et saisissez un nom de session.")
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.create_session({
            "nom_session": name,
            "mode": self.mode_var.get(),
            "questionnaire_id": questionnaire_id,
        }))
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if result is not None:
            self.name_var.set("")
            self.load_sessions()
            messagebox.showinfo("Session créée", "La session a été créée.")

    def load_sessions(self, _event=None) -> None:
        """
        Charge sessions et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        questionnaire_id = self._current_questionnaire_id()
        if questionnaire_id is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        sessions = run_api_action(lambda: self.api.list_sessions(questionnaire_id))
        if sessions is None:
            return
        self.sessions_by_id = {item["id"]: item for item in sessions}
        self.selected_session_id = None
        self.share_code_var.set("Code de partage : —")
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())
        # Met à jour le contenu du tableau affiché dans l'interface.
        for item in sessions:
            self.tree.insert("", "end", iid=str(item["id"]), values=(
                item["nom_session"], item["mode"], item.get("date_debut") or "—",
                item.get("date_fin") or "—", item["statut"],
            ))

    def _remember_selection(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à remember selection dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        self.selected_session_id = int(selection[0]) if selection else None

    def _require_session(self) -> int | None:
        """
        Effectue le traitement correspondant à require session dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_session_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez une session.")
        return self.selected_session_id

    def _load_participations_required(self, session_id: int) -> list[dict] | None:
        """
        Effectue le traitement correspondant à load participations required dans le contexte de cette fenêtre.
        
        Paramètres :
            session_id : identifiant de la session concernée.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        participations = run_api_action(lambda: self.api.list_participations(session_id))
        if participations is None:
            return None
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not participations:
            messagebox.showwarning(
                "Aucun participant",
                "Inscrivez au moins un participant avant de démarrer ou d'animer la session.",
            )
            return None
        return participations

    def start_session(self) -> None:
        """
        Démarre session et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self._require_session()
        if not session_id or self._load_participations_required(session_id) is None:
            return
        current = self.sessions_by_id.get(session_id, {})
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if current.get("statut") == "cloturee":
            messagebox.showwarning("Session clôturée", "Cette session est déjà clôturée.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if current.get("statut") == "en_cours":
            messagebox.showinfo("Session", "Cette session est déjà démarrée.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if run_api_action(lambda: self.api.start_session(session_id)) is not None:
            self.load_sessions()
            if self.tree.exists(str(session_id)):
                self.tree.selection_set(str(session_id))
                self.selected_session_id = session_id
            messagebox.showinfo("Session", "La session est maintenant ouverte aux réponses.")

    def animate_session(self) -> None:
        """
        Effectue le traitement correspondant à animate session dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self._require_session()
        if not session_id or self._load_participations_required(session_id) is None:
            return

        current = self.sessions_by_id.get(session_id, {})
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if current.get("statut") == "cloturee":
            messagebox.showwarning("Session clôturée", "Une session clôturée ne peut plus recevoir de réponses.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
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

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        code_payload = run_api_action(lambda: self.api.get_share_code(session_id))
        if not code_payload:
            return
        code = code_payload["code"]
        self.share_code_var.set(f"Code de partage : {code}")

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        public_session = run_api_action(lambda: self.api.open_public_session(session_id, code))
        if public_session is None:
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not public_session.get("participants_en_attente"):
            messagebox.showinfo(
                "Aucune réponse en attente",
                "Tous les participants inscrits ont déjà obtenu un score.",
            )
            return
        SessionPlayerWindow(self, public_session, session_id, code, current.get("mode", "individuel"))

    def close_session(self) -> None:
        """
        Effectue le traitement correspondant à close session dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self._require_session()
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        if session_id and run_api_action(lambda: self.api.close_session(session_id)) is not None:
            self.load_sessions()

    def show_share_code(self) -> None:
        """
        Affiche share code et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self._require_session()
        if not session_id:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.get_share_code(session_id))
        if result:
            self.share_code_var.set(f"Code de partage : {result['code']}")

    def manage_participations(self) -> None:
        """
        Effectue le traitement correspondant à manage participations dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self._require_session()
        if session_id:
            ParticipationWindow(self, self.api, session_id, self.sessions_by_id.get(session_id, {}).get("mode", "individuel"))


class SessionPlayerWindow(tk.Toplevel):
    """
    Représente session player window dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self, parent, public_session: dict, session_id: int, code: str, session_mode: str = "individuel") -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            public_session : donnée nécessaire au traitement de « public session ».
            session_id : identifiant de la session concernée.
            code : donnée nécessaire au traitement de « code ».
            session_mode : donnée nécessaire au traitement de « session mode ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent)
        self.parent = parent
        self.api = parent.api
        self.session_id = session_id
        self.code = code
        self.public_session = public_session
        self.session_mode = session_mode
        self.questions = public_session.get("questions") or []
        self.index = 0
        self.responses: dict[int, set[int]] = {}
        self.answer_buttons: list[tk.Button] = []
        self.default_button_bg: str | None = None
        self.seconds_left = 30
        self.running = False
        self.timer_job: str | None = None

        self.participant_var = tk.StringVar()
        self.participant_ids: dict[str, int] = {}
        self.progress_var = tk.StringVar()
        self.timer_var = tk.StringVar(value="00:30")
        self.duration_var = tk.IntVar(value=30)
        self.answer_feedback_var = tk.StringVar(value="Sélectionnez une ou plusieurs propositions.")

        self.title(f"Session — {public_session.get('titre_questionnaire', '')}")
        self.geometry("1000x740")
        self.minsize(800, 600)
        self.transient(parent.winfo_toplevel())

        self._create_widgets()
        self._load_participants(public_session.get("participants_en_attente") or [])
        if self.questions:
            self.show_question()
            messagebox.showinfo(
                "Démarrage du quiz",
                "Appuyez sur le bouton « Démarrer » du chronomètre avant de répondre.",
                parent=self,
            )
        else:
            self.question_label.config(text="Ce questionnaire ne contient aucune question.")
            self.answer_feedback_var.set("Ajoutez au moins une question avant d'animer la session.")
            self.previous_button.config(state="disabled")
            self.next_button.config(state="disabled")
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def _create_widgets(self) -> None:
        """
        Effectue le traitement correspondant à create widgets dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        scrollable = VerticalScrolledFrame(self)
        scrollable.pack(fill="both", expand=True)
        content = scrollable.content

        top = ttk.Frame(content, padding=14)
        top.pack(fill="x")
        ttk.Label(top, text=self.public_session.get("titre_questionnaire", "Questionnaire"), font=("Arial", 20, "bold")).pack(side="left")
        ttk.Label(top, textvariable=self.progress_var, font=("Arial", 12, "bold")).pack(side="right")

        participant_frame = ttk.LabelFrame(content, text="Participant qui répond", padding=10)
        participant_frame.pack(fill="x", padx=14, pady=(0, 8))
        ttk.Label(participant_frame, text="Participant :").pack(side="left")
        self.participant_combo = ttk.Combobox(
            participant_frame,
            textvariable=self.participant_var,
            state="readonly",
            width=42,
        )
        self.participant_combo.pack(side="left", padx=8)
        ttk.Label(
            participant_frame,
            text="Le score sera calculé et enregistré automatiquement à la fin.",
        ).pack(side="left", padx=12)

        timer_frame = ttk.LabelFrame(content, text="Minuteur", padding=10)
        timer_frame.pack(fill="x", padx=14)
        ttk.Label(timer_frame, text="Durée :").pack(side="left")
        ttk.Spinbox(timer_frame, from_=5, to=600, increment=5, textvariable=self.duration_var, width=7).pack(side="left", padx=5)
        ttk.Label(timer_frame, text="secondes").pack(side="left")
        ttk.Label(timer_frame, textvariable=self.timer_var, font=("Arial", 24, "bold")).pack(side="left", padx=25)
        ttk.Button(timer_frame, text="Démarrer", command=self.start_timer).pack(side="left", padx=3)
        ttk.Button(timer_frame, text="Pause / reprendre", command=self.toggle_pause).pack(side="left", padx=3)
        ttk.Button(timer_frame, text="Réinitialiser", command=self.reset_timer).pack(side="left", padx=3)

        question_frame = ttk.LabelFrame(content, text="Question affichée", padding=18)
        question_frame.pack(fill="both", expand=True, padx=14, pady=12)
        self.question_label = ttk.Label(question_frame, text="", font=("Arial", 18, "bold"), wraplength=900, justify="center")
        self.question_label.pack(fill="x", pady=(10, 22))
        self.propositions_frame = ttk.Frame(question_frame)
        self.propositions_frame.pack(fill="both", expand=True)
        ttk.Label(
            question_frame,
            textvariable=self.answer_feedback_var,
            font=("Arial", 12, "bold"),
            anchor="center",
        ).pack(fill="x", pady=(8, 0))

        nav = ttk.Frame(content, padding=(14, 0, 14, 14))
        nav.pack(fill="x")
        self.previous_button = ttk.Button(nav, text="← Question précédente", command=self.previous_question)
        self.previous_button.pack(side="left")
        ttk.Button(nav, text="Passer la question", command=self.next_question).pack(side="left", padx=8)
        ttk.Button(nav, text="Retour", command=self.close_window).pack(side="right", padx=8)
        self.next_button = ttk.Button(nav, text="Question suivante →", command=self.next_question)
        self.next_button.pack(side="right")
        ttk.Button(nav, text="Participations / notes", command=self.open_participations).pack(side="right", padx=8)

    def _load_participants(self, participants: list[dict]) -> None:
        """
        Effectue le traitement correspondant à load participants dans le contexte de cette fenêtre.
        
        Paramètres :
            participants : donnée nécessaire au traitement de « participants ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.participant_ids = {
            item["nom_affiche"]: item["participation_id"] for item in participants
        }
        values = list(self.participant_ids)
        self.participant_combo["values"] = values
        self.participant_var.set(values[0] if values else "")

    def show_question(self) -> None:
        """
        Affiche question et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.stop_timer()
        self.reset_timer()
        question = self.questions[self.index]
        question_id = question["id"]
        self.progress_var.set(f"Question {self.index + 1} / {len(self.questions)}")
        self.question_label.config(text=question.get("enonce") or "Question sans énoncé")

        for widget in self.propositions_frame.winfo_children():
            widget.destroy()
        self.answer_buttons = []

        selected_ids = self.responses.get(question_id, set())
        propositions = question.get("propositions") or []
        if not propositions:
            ttk.Label(self.propositions_frame, text="Aucune proposition enregistrée.", font=("Arial", 13)).pack(pady=15)
        else:
            for number, proposition in enumerate(propositions, start=1):
                proposition_id = proposition["id"]
                button = tk.Button(
                    self.propositions_frame,
                    text=f"{number}.  {proposition.get('libelle') or ''}",
                    font=("Arial", 14),
                    wraplength=840,
                    justify="left",
                    anchor="w",
                    relief="sunken" if proposition_id in selected_ids else "raised",
                    bd=2,
                    padx=12,
                    pady=10,
                    cursor="hand2",
                    command=lambda pid=proposition_id: self.toggle_answer(pid),
                )
                button.pack(fill="x", pady=5)
                if self.default_button_bg is None:
                    self.default_button_bg = button.cget("bg")
                self.answer_buttons.append(button)
                self._style_answer_button(button, proposition_id in selected_ids)
                # Les réponses restent bloquées jusqu'au démarrage du chronomètre.
                button.config(state="disabled", cursor="arrow")

        self.answer_feedback_var.set("Appuyez sur « Démarrer » pour autoriser les réponses.")
        self.previous_button.config(state="normal" if self.index > 0 else "disabled")
        self.next_button.config(text="Terminer et corriger" if self.index == len(self.questions) - 1 else "Question suivante →")

    def toggle_answer(self, proposition_id: int) -> None:
        """
        Active ou désactive answer et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            proposition_id : donnée nécessaire au traitement de « proposition id ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Ignore toute tentative de réponse tant que le chronomètre n'est pas lancé.
        if not self.running:
            messagebox.showwarning(
                "Chronomètre non démarré",
                "Appuyez sur « Démarrer » avant de sélectionner une réponse.",
                parent=self,
            )
            return

        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not self.participant_var.get():
            messagebox.showwarning("Participant requis", "Choisissez d'abord le participant qui répond.", parent=self)
            return
        self.participant_combo.config(state="disabled")
        question_id = self.questions[self.index]["id"]
        selected = self.responses.setdefault(question_id, set())
        if proposition_id in selected:
            selected.remove(proposition_id)
        else:
            selected.add(proposition_id)
        for button, proposition in zip(self.answer_buttons, self.questions[self.index].get("propositions") or []):
            self._style_answer_button(button, proposition["id"] in selected)
        self._update_feedback()

    def _style_answer_button(self, button: tk.Button, selected: bool) -> None:
        """
        Effectue le traitement correspondant à style answer button dans le contexte de cette fenêtre.
        
        Paramètres :
            button : donnée nécessaire au traitement de « button ».
            selected : donnée nécessaire au traitement de « selected ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if selected:
            button.config(bg="#cfe8ff", activebackground="#cfe8ff", relief="sunken")
        else:
            button.config(bg=self.default_button_bg or "SystemButtonFace", relief="raised")

    def _update_feedback(self) -> None:
        """
        Effectue le traitement correspondant à update feedback dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        question_id = self.questions[self.index]["id"]
        count = len(self.responses.get(question_id, set()))
        if count == 0:
            self.answer_feedback_var.set("Aucune proposition sélectionnée pour cette question.")
        elif count == 1:
            self.answer_feedback_var.set("1 proposition sélectionnée.")
        else:
            self.answer_feedback_var.set(f"{count} propositions sélectionnées.")

    def start_timer(self) -> None:
        """
        Démarre timer et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.running:
            return
        if self.seconds_left <= 0:
            self.reset_timer()
        self.running = True
        for button in self.answer_buttons:
            button.config(state="normal", cursor="hand2")
        self._update_feedback()
        self.tick()

    def toggle_pause(self) -> None:
        """
        Active ou désactive pause et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def reset_timer(self) -> None:
        """
        Réinitialise timer et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.stop_timer()
        try:
            self.seconds_left = max(1, int(self.duration_var.get()))
        except (ValueError, tk.TclError):
            self.seconds_left = 30
            self.duration_var.set(30)
        self.update_timer_label()

    def tick(self) -> None:
        """
        Effectue le traitement correspondant à tick dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.update_timer_label()
        if not self.running:
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.seconds_left <= 0:
            self.running = False
            for button in self.answer_buttons:
                button.config(state="disabled", cursor="arrow")
            self.bell()
            messagebox.showinfo("Temps écoulé", "Le temps de réponse est écoulé.", parent=self)
            return
        self.seconds_left -= 1
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.timer_job = self.after(1000, self.tick)

    def update_timer_label(self) -> None:
        """
        Met à jour timer label et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        minutes, seconds = divmod(max(0, self.seconds_left), 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")

    def stop_timer(self) -> None:
        """
        Arrête timer et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.running = False
        for button in self.answer_buttons:
            button.config(state="disabled", cursor="arrow")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def previous_question(self) -> None:
        """
        Effectue le traitement correspondant à previous question dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def next_question(self) -> None:
        """
        Effectue le traitement correspondant à next question dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.show_question()
            return
        self.submit_answers()

    def submit_answers(self) -> None:
        """
        Envoie answers et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.stop_timer()
        participant_id = self.participant_ids.get(self.participant_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if participant_id is None:
            messagebox.showwarning("Participant requis", "Choisissez le participant qui répond.", parent=self)
            return
        unanswered = sum(1 for q in self.questions if not self.responses.get(q["id"]))
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if unanswered and not messagebox.askyesno(
            "Questions sans réponse",
            f"{unanswered} question(s) n'ont aucune réponse. Les soumettre ainsi ?",
            parent=self,
        ):
            return
        payload = {
            "participation_id": participant_id,
            "reponses": [
                {
                    "question_id": question["id"],
                    "proposition_ids": sorted(self.responses.get(question["id"], set())),
                }
                for question in self.questions
            ],
        }
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(
            lambda: self.api.submit_public_answers(self.session_id, self.code, payload)
        )
        if result is None:
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo(
            "Correction terminée",
            f"Score enregistré automatiquement : {result['score_sur_20']} / 20\n"
            f"Bonnes réponses : {result['nombre_correctes']} / {result['nombre_questions']}",
            parent=self,
        )
        self._prepare_next_participant()

    def _prepare_next_participant(self) -> None:
        """
        Effectue le traitement correspondant à prepare next participant dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        public_session = run_api_action(lambda: self.api.open_public_session(self.session_id, self.code))
        if public_session is None:
            return
        participants = public_session.get("participants_en_attente") or []
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not participants:
            messagebox.showinfo("Session", "Tous les participants inscrits ont répondu.", parent=self)
            self.destroy()
            return
        self.public_session = public_session
        self.questions = public_session.get("questions") or []
        self.responses.clear()
        self.index = 0
        self.participant_combo.config(state="readonly")
        self._load_participants(participants)
        self.show_question()

    def open_participations(self) -> None:
        """
        Ouvre participations et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        ParticipationWindow(self, self.api, self.session_id, self.session_mode)

    def close_window(self) -> None:
        """
        Effectue le traitement correspondant à close window dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.stop_timer()
        self.destroy()


class ParticipationWindow(tk.Toplevel):
    """
    Représente participation window dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self, parent, api, session_id: int, session_mode: str = "individuel") -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            api : client de communication utilisé par la fenêtre.
            session_id : identifiant de la session concernée.
            session_mode : donnée nécessaire au traitement de « session mode ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent)
        self.api = api
        self.session_id = session_id
        self.session_mode = session_mode
        self.title("Participations et notes")
        self.geometry("940x690")
        self.minsize(800, 560)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.niveau_var = tk.StringVar()
        self.eleve_var = tk.StringVar()
        self.equipe_name_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.initial_comment_var = tk.StringVar()
        self.final_comment_var = tk.StringVar()
        self.selected_members_var = tk.StringVar(value="Aucun membre sélectionné.")
        self.niveau_ids: dict[str, int] = {}
        self.niveau_choice_ids: list[int] = []
        self.niveaux: list[dict] = []
        self.etablissement_names_by_id: dict[int, str] = {}
        self.eleve_ids: dict[str, int] = {}
        self.eleves_by_index: list[tuple[str, int]] = []
        self.participations: dict[int, dict] = {}
        self.participant_names: dict[int, str] = {}
        self.team_members_by_participant: dict[int, list[str]] = {}

        self._create_widgets()
        self.load_niveaux()
        self.load_participations()

    def _create_widgets(self) -> None:
        """
        Effectue le traitement correspondant à create widgets dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        scrollable = VerticalScrolledFrame(self)
        scrollable.pack(fill="both", expand=True)
        content = scrollable.content

        title = "Inscrire une équipe" if self.session_mode == "equipe" else "Inscrire un élève"
        registration = ttk.LabelFrame(content, text=title, padding=10)
        registration.pack(fill="x", padx=12, pady=12)

        ttk.Label(registration, text="Niveau / établissement :").grid(row=0, column=0, sticky="nw", pady=4)
        self.niveau_combo = ttk.Combobox(registration, textvariable=self.niveau_var, state="readonly")
        self.niveau_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.niveau_combo.bind("<<ComboboxSelected>>", self.load_eleves)

        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        if self.session_mode == "equipe":
            ttk.Label(registration, text="Nom de l'équipe :").grid(row=1, column=0, sticky="w", pady=4)
            ttk.Entry(registration, textvariable=self.equipe_name_var).grid(row=1, column=1, sticky="ew", padx=5, pady=4)
            ttk.Label(registration, text="Membres :").grid(row=2, column=0, sticky="nw", pady=4)
            members_frame = ttk.Frame(registration)
            members_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=4)
            self.members_listbox = tk.Listbox(members_frame, selectmode="multiple", height=7, exportselection=False)
            self.members_listbox.pack(side="left", fill="both", expand=True)
            self.members_listbox.bind("<<ListboxSelect>>", self._update_selected_members)
            scrollbar = ttk.Scrollbar(members_frame, orient="vertical", command=self.members_listbox.yview)
            scrollbar.pack(side="right", fill="y")
            self.members_listbox.configure(yscrollcommand=scrollbar.set)
            ttk.Label(
                registration,
                text="Cliquez sur chaque élève pour l'ajouter ou le retirer de l'équipe.",
            ).grid(row=3, column=1, sticky="w", padx=5)
            ttk.Label(
                registration,
                textvariable=self.selected_members_var,
                wraplength=720,
                justify="left",
            ).grid(row=4, column=1, sticky="ew", padx=5, pady=(2, 5))
            comment_row = 5
            button_row = 6
        else:
            ttk.Label(registration, text="Élève :").grid(row=1, column=0, sticky="w", pady=4)
            self.eleve_combo = ttk.Combobox(registration, textvariable=self.eleve_var, state="readonly")
            self.eleve_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
            comment_row = 2
            button_row = 3

        ttk.Label(registration, text="Commentaire initial :").grid(row=comment_row, column=0, sticky="w", pady=4)
        ttk.Entry(registration, textvariable=self.initial_comment_var).grid(row=comment_row, column=1, sticky="ew", padx=5, pady=4)
        ttk.Button(registration, text="Inscrire", command=self.add_participation).grid(
            row=button_row, column=0, columnspan=2, pady=6
        )
        registration.columnconfigure(1, weight=1)

        frame = ttk.LabelFrame(content, text="Participations de la session", padding=8)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tree_container = ttk.Frame(frame)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style(self)
        # Hauteur compacte : assez grande pour 2 à 3 lignes sans créer de gros espaces.
        style.configure(
            "Participation.Treeview",
            rowheight=54,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Participation.Treeview.Heading",
            anchor="center",
            relief="raised",
        )
        self.tree = ttk.Treeview(
            tree_container,
            columns=("participant", "score", "commentaire_initial", "commentaire_final"),
            show="headings",
            selectmode="browse",
            style="Participation.Treeview",
        )
        # Colonnes équilibrées : participant à gauche, score et commentaires centrés.
        for name, title, width, anchor, stretch in (
            ("participant", "Participant / membres", 330, "w", True),
            ("score", "Score / 20", 95, "center", False),
            ("commentaire_initial", "Commentaire initial", 300, "center", True),
            ("commentaire_final", "Commentaire final", 360, "center", True),
        ):
            self.tree.heading(name, text=title, anchor="center")
            self.tree.column(
                name,
                width=width,
                minwidth=80,
                anchor=anchor,
                stretch=stretch,
            )

        # Alternance visuelle pour distinguer nettement chaque participation.
        self.tree.tag_configure("even", background="#f2f2f2")
        self.tree.tag_configure("odd", background="#ffffff")
        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_evaluation)

        evaluation = ttk.LabelFrame(frame, text="Évaluation manuelle (facultative)", padding=8)
        evaluation.pack(fill="x", pady=(8, 0))
        ttk.Label(evaluation, text="Score / 20 :").grid(row=0, column=0, sticky="w")
        ttk.Entry(evaluation, textvariable=self.score_var, width=10).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(evaluation, text="Commentaire final :").grid(row=1, column=0, sticky="w", pady=(7, 0))
        ttk.Entry(evaluation, textvariable=self.final_comment_var).grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=(7, 0)
        )
        ttk.Button(
            evaluation,
            text="Enregistrer score et commentaire",
            command=self.evaluate,
        ).grid(row=0, column=2, padx=6)
        ttk.Button(evaluation, text="Actualiser", command=self.load_participations).grid(row=0, column=3, padx=6)
        evaluation.columnconfigure(1, weight=1)

        footer = ttk.Frame(content)
        footer.pack(fill="x", padx=14, pady=(8, 14))
        ttk.Button(footer, text="Retour", command=self.destroy).pack(side="right")

    def _refresh_niveau_choices(self) -> None:
        """
        Effectue le traitement correspondant à refresh niveau choices dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        labels: list[str] = []
        self.niveau_choice_ids = []

        shared_names = getattr(self.api, "etablissement_names_by_id", {})
        self.etablissement_names_by_id.update(shared_names)

        for item in self.niveaux:
            etablissement_id = item.get("etablissement_id")
            school = self.etablissement_names_by_id.get(
                etablissement_id,
                f"Établissement {etablissement_id}",
            )
            labels.append(f"{item['nom_niveau']} — {school}")
            self.niveau_choice_ids.append(item["id"])

        self.niveau_combo["values"] = labels
        if labels:
            self.niveau_combo.current(0)
        else:
            self.niveau_var.set("")
        self.load_eleves()

    def load_niveaux(self) -> None:
        """
        Charge niveaux et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        items = run_api_action(self.api.list_niveaux)
        if items is None:
            return
        self.niveaux = items
        self._refresh_niveau_choices()

    def load_eleves(self, _event=None) -> None:
        """
        Charge eleves et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        index = self.niveau_combo.current()
        if index < 0 or index >= len(self.niveau_choice_ids):
            return
        niveau_id = self.niveau_choice_ids[index]
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        items = run_api_action(lambda: self.api.list_eleves(niveau_id))
        if items is None:
            return

        self.eleve_ids = {}
        self.eleves_by_index = []
        labels: list[str] = []
        for item in items:
            name = f"{item.get('prenom') or ''} {item.get('nom_eleve') or ''}".strip() or f"Élève {item['id']}"
            label = f"{name} — ID {item['id']}"
            self.eleve_ids[label] = item["id"]
            self.eleves_by_index.append((label, item["id"]))
            self.participant_names[item["id"]] = name
            labels.append(label)

        if self.session_mode == "equipe":
            self.members_listbox.delete(0, "end")
            for label in labels:
                self.members_listbox.insert("end", label)
        else:
            self.eleve_combo["values"] = labels
            self.eleve_var.set(labels[0] if labels else "")

    def _update_selected_members(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à update selected members dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.session_mode != "equipe":
            return
        selected = self.members_listbox.curselection()
        names = [self.eleves_by_index[index][0].split(" — ID ", 1)[0] for index in selected]
        if not names:
            self.selected_members_var.set("Aucun membre sélectionné.")
        else:
            self.selected_members_var.set("Membres sélectionnés : " + ", ".join(names))

    @staticmethod
    def _member_name(member: dict) -> str:
        """
        Effectue le traitement correspondant à member name dans le contexte de cette fenêtre.
        
        Paramètres :
            member : donnée nécessaire au traitement de « member ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return f"{member.get('prenom') or ''} {member.get('nom_eleve') or ''}".strip() or f"Élève {member.get('id', '?')}"

    def _team_display_name(self, team: dict, fallback_id: int | None = None) -> str:
        """
        Effectue le traitement correspondant à team display name dans le contexte de cette fenêtre.
        
        Paramètres :
            team : donnée nécessaire au traitement de « team ».
            fallback_id : donnée nécessaire au traitement de « fallback id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        name = team.get("nom_equipe") or (f"Équipe {fallback_id}" if fallback_id is not None else "Équipe")
        members = [self._member_name(member) for member in (team.get("membres") or [])]
        if fallback_id is not None:
            self.team_members_by_participant[fallback_id] = members
        return f"{name} : {', '.join(members)}" if members else name

    def add_participation(self) -> None:
        """
        Ajoute participation et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        initial_comment = self.initial_comment_var.get().strip() or None

        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.session_mode == "equipe":
            team_name = self.equipe_name_var.get().strip()
            selected = self.members_listbox.curselection()
            if not team_name:
                messagebox.showwarning("Nom requis", "Saisissez un nom pour l'équipe.", parent=self)
                return
            if not selected:
                messagebox.showwarning("Membres requis", "Sélectionnez au moins un élève.", parent=self)
                return
            eleve_ids = [self.eleves_by_index[index][1] for index in selected]
            equipe = run_api_action(
                lambda: self.api.create_equipe(
                    {"nom_equipe": team_name, "eleve_ids": eleve_ids, "cours_id": None}
                )
            )
            if not isinstance(equipe, dict):
                return
            participant_id = equipe["id"]
            self.participant_names[participant_id] = self._team_display_name(equipe, participant_id)
        else:
            participant_id = self.eleve_ids.get(self.eleve_var.get())
            if participant_id is None:
                messagebox.showwarning("Aucun élève", "Choisissez un élève.", parent=self)
                return

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(
            lambda: self.api.create_participation(
                self.session_id,
                {"participant_id": participant_id, "commentaire_initial": initial_comment},
            )
        )
        if result is None:
            return

        self.initial_comment_var.set("")
        if self.session_mode == "equipe":
            self.equipe_name_var.set("")
            self.members_listbox.selection_clear(0, "end")
            self._update_selected_members()
            message = "L'équipe a été créée puis inscrite comme un seul participant."
        else:
            message = "L'élève a été inscrit."
        self.load_participations()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Participation", message, parent=self)

    def _participant_name(self, participant_id: int) -> str:
        """
        Effectue le traitement correspondant à participant name dans le contexte de cette fenêtre.
        
        Paramètres :
            participant_id : donnée nécessaire au traitement de « participant id ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if participant_id in self.participant_names:
            return self.participant_names[participant_id]

        # Le mode de la session indique le type concret du participant.
        # Cela évite d'appeler la route élève avec l'identifiant d'une équipe.
        if self.session_mode == "equipe":
            participant = run_api_action(lambda: self.api.get_equipe(participant_id))
            if isinstance(participant, dict):
                name = self._team_display_name(participant, participant_id)
                self.participant_names[participant_id] = name
                return name
        else:
            participant = run_api_action(lambda: self.api.get_eleve(participant_id))
            if isinstance(participant, dict):
                name = f"{participant.get('prenom') or ''} {participant.get('nom_eleve') or ''}".strip()
                if name:
                    self.participant_names[participant_id] = name
                    return name

        return f"Participant {participant_id}"

    @staticmethod
    def _wrap_table_text(value, width: int) -> str:
        """
        Effectue le traitement correspondant à wrap table text dans le contexte de cette fenêtre.
        
        Paramètres :
            value : donnée nécessaire au traitement de « value ».
            width : donnée nécessaire au traitement de « width ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        text = "" if value is None else str(value).strip()
        if not text:
            return ""
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            lines.extend(
                wrap(
                    paragraph,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False,
                ) or [""]
            )
        return "\n".join(lines[:3])

    @staticmethod
    def _wrap_participant_text(value, width: int = 32) -> str:
        """
        Répartit le nom d'un participant sur plusieurs lignes lorsque le texte
        dépasse la largeur de la colonne. Cette présentation est surtout utile
        pour les équipes comprenant plusieurs membres.

        Paramètres :
            value : nom de l'élève ou texte complet de l'équipe.
            width : nombre approximatif de caractères par ligne.

        Retour :
            Texte complet avec des retours à la ligne, sans supprimer de membre.
        """
        text = "" if value is None else str(value).strip()
        if not text:
            return ""
        return "\n".join(
            wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
            or [text]
        )

    def load_participations(self) -> None:
        """
        Charge participations et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        items = run_api_action(lambda: self.api.list_participations(self.session_id))
        if items is None:
            return
        self.participations = {item["id"]: item for item in items}
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())

        # Prépare les textes avant l'insertion afin d'adapter la hauteur des lignes
        # au nombre réel de lignes nécessaires pour afficher toutes les équipes.
        prepared_rows = []
        maximum_line_count = 1
        for row_index, item in enumerate(items):
            participant_text = self._wrap_participant_text(
                self._participant_name(item["participant_id"])
            )
            maximum_line_count = max(
                maximum_line_count,
                participant_text.count("\n") + 1,
            )
            prepared_rows.append((row_index, item, participant_text))

        ttk.Style(self).configure(
            "Participation.Treeview",
            rowheight=max(54, maximum_line_count * 19),
        )

        for row_index, item, participant_text in prepared_rows:
            row_tag = "even" if row_index % 2 == 0 else "odd"
            self.tree.insert(
                "",
                "end",
                iid=str(item["id"]),
                tags=(row_tag,),
                values=(
                    participant_text,
                    "—" if item.get("score") is None else item["score"],
                    self._wrap_table_text(item.get("commentaire_initial"), 34),
                    self._wrap_table_text(item.get("commentaire_final"), 46),
                ),
            )

    def load_selected_evaluation(self, _event=None) -> None:
        """
        Charge selected evaluation et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        if not selection:
            return
        item = self.participations.get(int(selection[0]), {})
        self.score_var.set("" if item.get("score") is None else str(item["score"]))
        self.final_comment_var.set(item.get("commentaire_final") or "")

    def evaluate(self) -> None:
        """
        Effectue le traitement correspondant à evaluate dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez une participation.", parent=self)
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        try:
            score = float(self.score_var.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Score invalide", "Saisissez un nombre.", parent=self)
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not 0 <= score <= 20:
            messagebox.showwarning("Score invalide", "Le score doit être compris entre 0 et 20.", parent=self)
            return
        participation_id = int(selection[0])
        comment = self.final_comment_var.get().strip() or None
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(
            lambda: self.api.evaluate_participation(
                participation_id,
                {"score": score, "commentaire_final": comment},
            )
        )
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if result is not None:
            self.load_participations()
            if self.tree.exists(str(participation_id)):
                self.tree.selection_set(str(participation_id))
            messagebox.showinfo("Évaluation", "La note et le commentaire ont été enregistrés.", parent=self)

