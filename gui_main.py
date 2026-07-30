# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Point d'entrée de l'application et contrôleur de navigation entre les écrans.

"""
Fichier principal de l'application QuizzenClasse.

Version GUI : 1.1

Ce fichier ne contient aucune logique métier : c'est juste le point de
départ qui ouvre la fenêtre et bascule d'un écran à l'autre. Chaque écran
réel (formulaires, tableaux, etc.) est défini dans son propre fichier sous
gui/, importé ci-dessous.
"""

import tkinter as tk

# Les 6 écrans de l'application, un par fonctionnalité. Ce sont des imports
# de compatibilité (gui/xxx_window.py) qui pointent vers les vrais fichiers,
# éventuellement découpés en sous-modules (ex : gui/eleves/).
from gui.dashboard_window import DashboardWindow      # tableau de bord (accueil après connexion)
from gui.cours_window import CoursWindow              # gestion des cours (pas de bouton dans le dashboard, voir show_cours)
from gui.eleves_window import ElevesWindow            # gestion des niveaux + élèves
from gui.login_window import LoginWindow              # connexion / création de compte
from gui.questionnaires_window import QuestionnairesWindow  # création des QCM
from gui.session_window import SessionWindow          # lancement et suivi des sessions de quiz
from gui.statistiques_window import StatistiquesWindow  # consultation des stats et export

# Deux façons de parler à l'API selon config.USE_API : soit un vrai client
# HTTP (ApiClient, vers le serveur FastAPI de l'équipe), soit une version
# hors-ligne pour dépanner sans serveur lancé (LocalClient, incomplète,
# voir services/local_client.py). Les deux ont les mêmes méthodes, donc le
# reste du code n'a pas besoin de savoir lequel des deux est actif.
from client.client import ApiClient
from config import USE_API
from services.local_client import LocalClient
from services.data_store import DataStore  # ancien stockage local, plus utilisé par la GUI (voir services/data_store.py)


class QuizzenClasseApp(tk.Tk):
    """Fenêtre racine de l'application : contrôleur de navigation entre les différents écrans.

    Chaque méthode ``show_...`` vide la fenêtre courante puis y affiche un
    nouvel écran ; c'est le seul point de l'application qui connaît la
    liste complète des écrans et l'ordre de navigation entre eux.
    """

    def __init__(self) -> None:
        """Configure la fenêtre principale, instancie le client API (réseau ou local) puis affiche l'écran de connexion."""
        super().__init__()

        self.title("QuizzenClasse")
        self.minsize(700, 500)
        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_application,
        )

        self.current_user = {}
        # Même interface dans les deux modes : réseau ou mémoire locale.
        self.api_client = ApiClient() if USE_API else LocalClient()
        self.data_store = DataStore()

        self.show_login()

    def clear_window(self) -> None:
        """Détruit tous les widgets actuellement affichés, avant de basculer vers un autre écran."""

        for widget in list(self.winfo_children()):
            try:
                widget.destroy()
            except tk.TclError:
                # Le widget peut avoir été fermé par l'utilisateur entre-temps.
                continue

    def center_window(
        self,
        width,
        height,
    ) -> None:
        """Redimensionne la fenêtre à ``width``x``height`` et la centre sur l'écran.

        Paramètres :
            width : largeur souhaitée de la fenêtre, en pixels.
            height : hauteur souhaitée de la fenêtre, en pixels.
        """

        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        position_x = max(
            (screen_width - width) // 2,
            0,
        )

        position_y = max(
            (screen_height - height) // 2,
            0,
        )

        self.geometry(
            f"{width}x{height}+{position_x}+{position_y}"
        )

    def show_login(self) -> None:
        """Affiche l'écran de connexion (700x500)."""

        self.clear_window()
        self.center_window(700, 500)
        LoginWindow(self)

    def show_dashboard(self) -> None:
        """Affiche le tableau de bord (800x580)."""

        self.clear_window()
        self.center_window(800, 580)
        DashboardWindow(self)

    def show_eleves(self) -> None:
        """Affiche l'écran de gestion des niveaux et élèves (1300x850, deux panneaux côte à côte)."""

        self.clear_window()
        self.center_window(1300, 850)
        ElevesWindow(self)

    def show_cours(self) -> None:
        """Affiche l'écran de gestion des cours (1000x700).

        Non relié à un bouton du tableau de bord (voir
        ``gui/dashboard_window.py``) ; conservé accessible par cette
        méthode au cas où l'entité serait exploitée plus tard.
        """

        self.clear_window()
        self.center_window(1000, 700)
        CoursWindow(self)

    def show_questionnaires(self) -> None:
        """Affiche l'écran de gestion des questionnaires (1000x700)."""

        self.clear_window()
        self.center_window(1000, 700)
        QuestionnairesWindow(self)

    def show_session(self) -> None:
        """Affiche l'écran de création et de suivi des sessions (1000x700)."""

        self.clear_window()
        self.center_window(1000, 700)
        SessionWindow(self)

    def show_statistiques(self) -> None:
        """Affiche l'écran de consultation des statistiques (1000x700)."""

        self.clear_window()
        self.center_window(1000, 700)
        StatistiquesWindow(self)

    def close_application(self) -> None:
        """Ferme proprement l'application (appelé aussi par le bouton de fermeture de la fenêtre)."""

        self.quit()
        self.destroy()

    def logout(self) -> None:
        """Déconnecte l'utilisateur courant (efface le profil et le jeton d'authentification) et revient à l'écran de connexion."""

        self.current_user = {}
        self.api_client.token = None
        self.show_login()



def main() -> None:
    """Point d'entrée de l'application : instancie ``QuizzenClasseApp`` et lance la boucle d'événements Tkinter."""
    application = QuizzenClasseApp()
    application.mainloop()


if __name__ == "__main__":
    main()
