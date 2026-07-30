# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Tableau d'affichage des questions préparées ou enregistrées.

"""Tableau court chargé d'afficher les questions préparées.

Fait équipe avec ``QuestionForm`` (qui ajoute les questions) dans
``QuestionnairesWindow`` : ce fichier ne fait qu'afficher et relayer les
clics, toute la validation et les appels API restent dans la fenêtre parente.
"""

from tkinter import ttk


class QuestionsTable(ttk.LabelFrame):
    """Tableau récapitulatif des questions d'un questionnaire (énoncé, nombre de propositions, bonnes réponses).

    Ne stocke aucune donnée elle-même : ``refresh`` reçoit la liste des
    questions à afficher, et les actions (suppression, ajout de proposition)
    sont déléguées à l'écran parent via les callbacks du constructeur.
    """

    def __init__(self, parent, on_delete, on_add_proposition=None) -> None:
        """Construit le tableau et sa barre d'actions.

        Paramètres :
            parent : widget parent qui contient ce tableau.
            on_delete : fonction appelée avec l'index de la ligne sélectionnée
                lors d'une suppression.
            on_add_proposition : fonction appelée avec l'index de la ligne
                sélectionnée pour ajouter une proposition ; si ``None``, le
                bouton correspondant n'est pas affiché.
        """
        super().__init__(parent, text="Questions préparées", padding=8)
        self.on_delete = on_delete
        self.on_add_proposition = on_add_proposition

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("enonce", "propositions", "correctes"),
            show="headings",
            height=9,
        )
        self.tree.heading("enonce", text="Énoncé")
        self.tree.heading("propositions", text="Propositions")
        self.tree.heading("correctes", text="Bonnes réponses")
        self.tree.column("enonce", width=420, minwidth=180, stretch=True)
        self.tree.column(
            "propositions", width=95, minwidth=95, anchor="center", stretch=False
        )
        self.tree.column(
            "correctes", width=135, minwidth=135, anchor="center", stretch=False
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(
            actions,
            text="Supprimer la question sélectionnée",
            command=self._delete,
        ).pack(side="left", padx=3)
        if self.on_add_proposition is not None:
            ttk.Button(
                actions,
                text="Ajouter une réponse à la question",
                command=self._add_proposition,
            ).pack(side="left", padx=3)

    def refresh(self, questions: list[dict]) -> None:
        """Repeuple le tableau à partir de la liste de questions fournie.

        L'identifiant de ligne (``iid``) est l'index de la question dans la
        liste : c'est cet index, et non un identifiant API, qui est transmis
        aux callbacks ``on_delete``/``on_add_proposition``.
        """
        self.tree.delete(*self.tree.get_children())
        for index, question in enumerate(questions):
            correctes = sum(p["est_correcte"] for p in question["propositions"])
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(question["enonce"], len(question["propositions"]), correctes),
            )

    def _delete(self) -> None:
        """Transmet à ``on_delete`` l'index de la question sélectionnée, si une ligne est sélectionnée."""
        selection = self.tree.selection()
        if selection:
            self.on_delete(int(selection[0]))

    def _add_proposition(self) -> None:
        """Transmet à ``on_add_proposition`` l'index de la question sélectionnée, si une ligne est sélectionnée."""
        selection = self.tree.selection()
        if selection and self.on_add_proposition is not None:
            self.on_add_proposition(int(selection[0]))
