# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Tableau d'affichage des questions préparées ou enregistrées.

"""Tableau court chargé d'afficher les questions préparées."""

from tkinter import ttk


class QuestionsTable(ttk.LabelFrame):
    """
    Représente questions table dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent, on_delete, on_add_proposition=None) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            on_delete : donnée nécessaire au traitement de « on delete ».
            on_add_proposition : donnée nécessaire au traitement de « on add proposition ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
        """
        Recharge les données affichées afin de présenter l'état le plus récent de l'application.
        
        Paramètres :
            questions : donnée nécessaire au traitement de « questions ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())
        # Met à jour le contenu du tableau affiché dans l'interface.
        for index, question in enumerate(questions):
            correctes = sum(p["est_correcte"] for p in question["propositions"])
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(question["enonce"], len(question["propositions"]), correctes),
            )

    def _delete(self) -> None:
        """
        Effectue le traitement correspondant à delete dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        if selection:
            self.on_delete(int(selection[0]))

    def _add_proposition(self) -> None:
        """
        Effectue le traitement correspondant à add proposition dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        if selection and self.on_add_proposition is not None:
            self.on_add_proposition(int(selection[0]))
