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
    """
    Représente dashboard window dans l'interface graphique QuizzenClasse.
    
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
        """
        Crée header et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Crée navigation buttons et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
            # Le module Cours n’est pas affiché dans le tableau de bord actuel : ses opérations de base
            # sont conservées dans le code, mais il n'est pas encore relié aux
            # niveaux, questionnaires ou sessions par les services disponibles.
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
        """
        Crée footer et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
