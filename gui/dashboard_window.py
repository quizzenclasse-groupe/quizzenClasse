# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Tableau de bord donnant accès aux modules fonctionnels.

"""
Tableau de bord principal de QuizzenClasse.

Cette fenêtre donne accès aux différents modules de l'application :
    - gestion des niveaux et des élèves ;
    - création des questionnaires ;
    - lancement des sessions ;
    - consultation des statistiques.
"""

from tkinter import ttk


class DashboardWindow(ttk.Frame):
    """Écran d'accueil affiché après connexion : identité de l'enseignant et boutons de navigation.

    Ne contient aucune logique métier propre : chaque bouton délègue
    directement à une méthode ``show_...`` de la fenêtre racine
    (``parent``), qui se charge de basculer vers l'écran correspondant.
    """

    def __init__(self, parent) -> None:
        """Construit l'en-tête, les boutons de navigation puis le pied de page.

        Paramètres :
            parent : fenêtre racine de l'application, qui porte
                ``current_user`` ainsi que les méthodes ``show_...`` et
                ``logout`` utilisées par les boutons de cet écran.
        """

        super().__init__(
            parent,
            padding=20,
        )

        self.parent = parent

        # grid est utilisé pour garantir que le contenu reste visible,
        # même lorsque la fenêtre est redimensionnée.

        self.pack(
            fill="both",
            expand=True,
        )
        self.parent.rowconfigure(
            0,
            weight=1,
        )
        self.parent.columnconfigure(
            0,
            weight=1,
        )

        self.columnconfigure(
            0,
            weight=1,
        )

        self.create_header()
        self.create_navigation_buttons()
        self.create_footer()

    def create_header(self) -> None:
        """Construit le titre, le nom de l'enseignant connecté et son établissement."""

        header_frame = ttk.Frame(self)

        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(10, 20),
        )

        header_frame.columnconfigure(
            0,
            weight=1,
        )

        ttk.Label(
            header_frame,
            text="Tableau de bord enseignant",
            font=("Arial", 20, "bold"),
            anchor="center",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 10),
        )

        user_name = self.parent.current_user.get(
            "nom",
            "Enseignant",
        )

        establishment = self.parent.current_user.get(
            "etablissement",
            "Non renseigné",
        )

        ttk.Label(
            header_frame,
            text=f"Bienvenue : {user_name}",
            font=("Arial", 12),
            anchor="center",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=2,
        )

        ttk.Label(
            header_frame,
            text=f"Établissement : {establishment}",
            anchor="center",
        ).grid(
            row=2,
            column=0,
            sticky="ew",
            pady=2,
        )

    def create_navigation_buttons(self) -> None:
        """Construit les boutons d'accès aux modules fonctionnels de l'application.

        Le module « Cours » n'apparaît volontairement pas dans cette liste
        (voir ``gui/cours/cours_window.py`` pour le détail de ce choix) :
        l'écran existe et fonctionne, mais n'est pas relié à la navigation.
        """

        navigation_frame = ttk.LabelFrame(
            self,
            text="Fonctionnalités",
            padding=15,
        )

        navigation_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=50,
            pady=10,
        )

        navigation_frame.columnconfigure(
            0,
            weight=1,
        )

        self.rowconfigure(
            1,
            weight=1,
        )

        buttons = (
            (
                "Gérer les niveaux et les élèves",
                self.parent.show_eleves,
            ),
            (
                "Créer un questionnaire",
                self.parent.show_questionnaires,
            ),
            (
                "Lancer une session de quiz",
                self.parent.show_session,
            ),
            (
                "Voir les statistiques et rapports",
                self.parent.show_statistiques,
            ),
        )

        for row_number, button_data in enumerate(buttons):
            button_text, button_command = button_data

            ttk.Button(
                navigation_frame,
                text=button_text,
                command=button_command,
            ).grid(
                row=row_number,
                column=0,
                sticky="ew",
                padx=10,
                pady=6,
                ipady=6,
            )

    def create_footer(self) -> None:
        """Construit les boutons « Changer d'utilisateur » et « Quitter l'application »."""

        footer_frame = ttk.Frame(self)

        footer_frame.grid(
            row=2,
            column=0,
            pady=(15, 5),
        )

        ttk.Button(
            footer_frame,
            text="Changer d'utilisateur",
            command=self.parent.logout,
        ).grid(
            row=0,
            column=0,
            padx=5,
        )

        ttk.Button(
            footer_frame,
            text="Quitter l'application",
            command=self.parent.destroy,
        ).grid(
            row=0,
            column=1,
            padx=5,
        )
