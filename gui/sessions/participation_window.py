# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Fenêtre de gestion des participations (inscription et évaluation).

"""Gestion des participations à une session : inscription des élèves ou des
équipes, puis saisie de la note et du commentaire final une fois la session
terminée.

Toutes les opérations passent par l'API REST : cette fenêtre n'effectue
aucun calcul de note, elle transmet les données saisies aux routes de
participation et de correction du backend.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from textwrap import wrap

from gui.common.messages import run_api_action
from gui.sessions.widgets import VerticalScrolledFrame


class ParticipationWindow(tk.Toplevel):
    """Fenêtre modale d'inscription et d'évaluation des participations d'une session.

    En mode ``"individuel"`` un élève est inscrit directement ; en mode
    ``"equipe"`` une équipe est d'abord créée via l'API à partir des élèves
    sélectionnés, puis inscrite comme participant unique.
    """

    def __init__(self, parent, api, session_id: int, session_mode: str = "individuel") -> None:
        """Prépare les variables Tkinter, construit l'interface puis charge les données.

        Paramètres :
            parent : widget parent (fenêtre appelante), utilisé pour rendre
                cette fenêtre modale (``transient`` + ``grab_set``).
            api : client HTTP utilisé pour tous les appels à l'API REST.
            session_id : identifiant de la session dont on gère les participations.
            session_mode : ``"individuel"`` ou ``"equipe"`` ; conditionne le
                formulaire d'inscription affiché (un élève ou une équipe).
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
        """Construit le formulaire d'inscription et le tableau des participations.

        Le formulaire varie selon ``self.session_mode`` : un simple menu
        déroulant d'élèves en mode individuel, ou un champ nom d'équipe plus
        une liste à sélection multiple des élèves à inclure en mode équipe.
        Le tableau ``self.tree`` liste ensuite chaque participation déjà
        enregistrée, avec un bloc de saisie du score et du commentaire final.
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
        # Changer de niveau recharge la liste des élèves de ce niveau.
        self.niveau_combo.bind("<<ComboboxSelected>>", self.load_eleves)

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
        # Sélectionner une ligne recharge son score/commentaire dans le formulaire d'évaluation.
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
        """Reconstruit les libellés du menu « Niveau / établissement » à partir de ``self.niveaux``.

        Chaque libellé combine le nom du niveau et celui de l'établissement
        (résolu via le cache partagé ``api.etablissement_names_by_id``), et
        déclenche ensuite le rechargement des élèves du premier niveau affiché.
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
        """Récupère la liste des niveaux de l'enseignant et rafraîchit le menu déroulant."""
        items = run_api_action(self.api.list_niveaux)
        if items is None:
            return
        self.niveaux = items
        self._refresh_niveau_choices()

    def load_eleves(self, _event=None) -> None:
        """Charge les élèves du niveau sélectionné dans le menu d'inscription ou la liste des membres.

        Alimente ``self.eleve_combo`` en mode individuel, ou
        ``self.members_listbox`` en mode équipe, selon ``self.session_mode``.
        """
        index = self.niveau_combo.current()
        if index < 0 or index >= len(self.niveau_choice_ids):
            return
        niveau_id = self.niveau_choice_ids[index]
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
        """Met à jour le texte récapitulatif des membres cochés dans la liste d'équipe."""
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
        """Construit le nom affichable d'un membre d'équipe à partir des données API (prénom + nom)."""
        return f"{member.get('prenom') or ''} {member.get('nom_eleve') or ''}".strip() or f"Élève {member.get('id', '?')}"

    def _team_display_name(self, team: dict, fallback_id: int | None = None) -> str:
        """Construit le libellé d'affichage d'une équipe : son nom suivi de la liste de ses membres.

        Met aussi à jour ``self.team_members_by_participant`` pour éviter de
        recalculer cette liste à chaque rafraîchissement du tableau.
        """
        name = team.get("nom_equipe") or (f"Équipe {fallback_id}" if fallback_id is not None else "Équipe")
        members = [self._member_name(member) for member in (team.get("membres") or [])]
        if fallback_id is not None:
            self.team_members_by_participant[fallback_id] = members
        return f"{name} : {', '.join(members)}" if members else name

    def add_participation(self) -> None:
        """Inscrit un élève, ou crée une équipe puis l'inscrit, comme participant de la session.

        En mode équipe, l'équipe est d'abord créée via ``api.create_equipe``
        à partir des élèves cochés ; son identifiant sert ensuite de
        ``participant_id`` pour l'inscription, exactement comme un élève seul.
        """
        initial_comment = self.initial_comment_var.get().strip() or None

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
        messagebox.showinfo("Participation", message, parent=self)

    def _participant_name(self, participant_id: int) -> str:
        """Résout le nom affichable d'un participant, avec mise en cache dans ``self.participant_names``.

        Le mode de la session indique le type concret du participant : cela
        évite d'appeler la route élève avec l'identifiant d'une équipe (ou
        inversement).
        """
        if participant_id in self.participant_names:
            return self.participant_names[participant_id]

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
        """Formate un commentaire pour la table : coupe le texte à ``width`` caractères par ligne, 3 lignes max."""
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
        """Répartit le nom d'un participant sur plusieurs lignes lorsque le texte
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
        """Recharge la liste des participations depuis l'API et repeuple le tableau.

        La hauteur des lignes du tableau est recalculée d'après le nombre de
        lignes nécessaires au nom le plus long (utile pour les équipes à
        plusieurs membres), afin qu'aucun texte ne soit tronqué à l'affichage.
        """
        items = run_api_action(lambda: self.api.list_participations(self.session_id))
        if items is None:
            return
        self.participations = {item["id"]: item for item in items}
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
        """Recopie le score et le commentaire final de la ligne sélectionnée dans le formulaire d'évaluation."""
        selection = self.tree.selection()
        if not selection:
            return
        item = self.participations.get(int(selection[0]), {})
        self.score_var.set("" if item.get("score") is None else str(item["score"]))
        self.final_comment_var.set(item.get("commentaire_final") or "")

    def evaluate(self) -> None:
        """Valide puis envoie le score et le commentaire final de la participation sélectionnée.

        Vérifie qu'une ligne est sélectionnée, que le score saisi est un
        nombre compris entre 0 et 20 (virgule ou point acceptés), avant
        d'appeler ``api.evaluate_participation``.
        """
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez une participation.", parent=self)
            return
        try:
            score = float(self.score_var.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Score invalide", "Saisissez un nombre.", parent=self)
            return
        if not 0 <= score <= 20:
            messagebox.showwarning("Score invalide", "Le score doit être compris entre 0 et 20.", parent=self)
            return
        participation_id = int(selection[0])
        comment = self.final_comment_var.get().strip() or None
        result = run_api_action(
            lambda: self.api.evaluate_participation(
                participation_id,
                {"score": score, "commentaire_final": comment},
            )
        )
        if result is not None:
            self.load_participations()
            if self.tree.exists(str(participation_id)):
                self.tree.selection_set(str(participation_id))
            messagebox.showinfo("Évaluation", "La note et le commentaire ont été enregistrés.", parent=self)
