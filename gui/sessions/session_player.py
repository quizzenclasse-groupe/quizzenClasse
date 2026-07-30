# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Fenêtre de déroulement d'une session de quiz (lecteur de questions).

"""Fenêtre de lecture d'une session de quiz.

Affiche les questions les unes après les autres, gère le minuteur, la
sélection des réponses et la soumission finale à l'API. Cette fenêtre ne
corrige rien elle-même : elle envoie les réponses choisies à la route de
soumission, qui renvoie la correction calculée côté serveur.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from gui.common.messages import run_api_action
from gui.sessions.participation_window import ParticipationWindow
from gui.sessions.widgets import VerticalScrolledFrame


class SessionPlayerWindow(tk.Toplevel):
    """Fenêtre de déroulement d'une session : un participant à la fois, question par question.

    Le flux est : choisir le participant qui répond → démarrer le minuteur →
    sélectionner les réponses → passer à la question suivante ou terminer,
    ce qui soumet les réponses à l'API et propose aussitôt le participant
    suivant en attente.
    """

    def __init__(self, parent, public_session: dict, session_id: int, code: str, session_mode: str = "individuel") -> None:
        """Initialise l'état du lecteur et affiche la première question.

        Paramètres :
            parent : fenêtre appelante (``SessionWindow``), dont ``api`` est réutilisé.
            public_session : session publique renvoyée par l'API à l'ouverture
                (questions, propositions, participants en attente).
            session_id : identifiant de la session animée.
            code : code de partage de la session, requis pour soumettre les réponses.
            session_mode : ``"individuel"`` ou ``"equipe"``, transmis tel quel
                à ``ParticipationWindow`` si l'enseignant l'ouvre depuis ici.
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
        """Construit l'écran de lecture : titre, sélecteur de participant, minuteur, zone de question et navigation."""
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
        """Alimente le menu déroulant des participants à partir de la liste des inscrits en attente."""
        self.participant_ids = {
            item["nom_affiche"]: item["participation_id"] for item in participants
        }
        values = list(self.participant_ids)
        self.participant_combo["values"] = values
        self.participant_var.set(values[0] if values else "")

    def show_question(self) -> None:
        """Affiche la question courante (``self.index``) : énoncé, boutons de proposition, navigation.

        Le minuteur est arrêté et réinitialisé à chaque changement de
        question, et les boutons de réponse restent désactivés tant que
        l'enseignant n'a pas relancé le chronomètre.
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
        """Ajoute ou retire une proposition de la réponse en cours de saisie pour la question affichée.

        Refuse la sélection tant que le chronomètre n'est pas démarré ou
        qu'aucun participant n'a été choisi, pour éviter d'enregistrer une
        réponse qui ne serait rattachable à personne.
        """
        if not self.running:
            messagebox.showwarning(
                "Chronomètre non démarré",
                "Appuyez sur « Démarrer » avant de sélectionner une réponse.",
                parent=self,
            )
            return

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
        """Applique le fond bleu clair aux propositions sélectionnées, la couleur par défaut sinon."""
        if selected:
            button.config(bg="#cfe8ff", activebackground="#cfe8ff", relief="sunken")
        else:
            button.config(bg=self.default_button_bg or "SystemButtonFace", relief="raised")

    def _update_feedback(self) -> None:
        """Met à jour le texte indiquant combien de propositions sont actuellement sélectionnées."""
        question_id = self.questions[self.index]["id"]
        count = len(self.responses.get(question_id, set()))
        if count == 0:
            self.answer_feedback_var.set("Aucune proposition sélectionnée pour cette question.")
        elif count == 1:
            self.answer_feedback_var.set("1 proposition sélectionnée.")
        else:
            self.answer_feedback_var.set(f"{count} propositions sélectionnées.")

    def start_timer(self) -> None:
        """Démarre (ou relance après expiration) le compte à rebours et active les boutons de réponse."""
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
        """Bascule entre pause et reprise du minuteur selon son état courant."""
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def reset_timer(self) -> None:
        """Réinitialise le compte à rebours à la durée choisie dans le champ « Durée » (30 s par défaut si invalide)."""
        self.stop_timer()
        try:
            self.seconds_left = max(1, int(self.duration_var.get()))
        except (ValueError, tk.TclError):
            self.seconds_left = 30
            self.duration_var.set(30)
        self.update_timer_label()

    def tick(self) -> None:
        """Décrémente le minuteur chaque seconde ; verrouille les réponses et alerte quand le temps est écoulé."""
        self.update_timer_label()
        if not self.running:
            return
        if self.seconds_left <= 0:
            self.running = False
            for button in self.answer_buttons:
                button.config(state="disabled", cursor="arrow")
            self.bell()
            messagebox.showinfo("Temps écoulé", "Le temps de réponse est écoulé.", parent=self)
            return
        self.seconds_left -= 1
        self.timer_job = self.after(1000, self.tick)

    def update_timer_label(self) -> None:
        """Formate ``self.seconds_left`` en ``MM:SS`` et met à jour l'affichage du minuteur."""
        minutes, seconds = divmod(max(0, self.seconds_left), 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")

    def stop_timer(self) -> None:
        """Arrête le compte à rebours et désactive les boutons de réponse (verrouillage entre deux questions)."""
        self.running = False
        for button in self.answer_buttons:
            button.config(state="disabled", cursor="arrow")
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def previous_question(self) -> None:
        """Revient à la question précédente, si ce n'est pas déjà la première."""
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def next_question(self) -> None:
        """Passe à la question suivante, ou lance la soumission des réponses si c'était la dernière."""
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.show_question()
            return
        self.submit_answers()

    def submit_answers(self) -> None:
        """Envoie les réponses du participant courant à l'API et affiche le score renvoyé par la correction.

        Demande confirmation si des questions ont été laissées sans réponse.
        La correction et le calcul du score sont entièrement faits côté
        serveur : cette méthode ne fait que transmettre les propositions
        cochées et afficher le résultat reçu.
        """
        self.stop_timer()
        participant_id = self.participant_ids.get(self.participant_var.get())
        if participant_id is None:
            messagebox.showwarning("Participant requis", "Choisissez le participant qui répond.", parent=self)
            return
        unanswered = sum(1 for q in self.questions if not self.responses.get(q["id"]))
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
        result = run_api_action(
            lambda: self.api.submit_public_answers(self.session_id, self.code, payload)
        )
        if result is None:
            return
        messagebox.showinfo(
            "Correction terminée",
            f"Score enregistré automatiquement : {result['score_sur_20']} / 20\n"
            f"Bonnes réponses : {result['nombre_correctes']} / {result['nombre_questions']}",
            parent=self,
        )
        self._prepare_next_participant()

    def _prepare_next_participant(self) -> None:
        """Recharge la session publique et enchaîne sur le participant suivant en attente, s'il y en a un.

        Ferme la fenêtre lorsque tous les participants inscrits ont répondu.
        """
        public_session = run_api_action(lambda: self.api.open_public_session(self.session_id, self.code))
        if public_session is None:
            return
        participants = public_session.get("participants_en_attente") or []
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
        """Ouvre la fenêtre de gestion des participations pour cette même session."""
        ParticipationWindow(self, self.api, self.session_id, self.session_mode)

    def close_window(self) -> None:
        """Arrête le minuteur puis ferme la fenêtre (appelé aussi par le bouton de fermeture de la fenêtre)."""
        self.stop_timer()
        self.destroy()
