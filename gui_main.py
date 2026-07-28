# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Point d'entrée de l'application et contrôleur de navigation entre les écrans.

"""
Fichier principal de l'application QuizzenClasse.

Version GUI : 1.1
"""

import tkinter as tk

from gui.dashboard_window import DashboardWindow
from gui.cours_window import CoursWindow
from gui.eleves_window import ElevesWindow
from gui.login_window import LoginWindow
from gui.questionnaires_window import QuestionnairesWindow
from gui.session_window import SessionWindow
from gui.statistiques_window import StatistiquesWindow
from client.client import ApiClient
from config import USE_API
from services.local_client import LocalClient
from services.data_store import DataStore


class QuizzenClasseApp(tk.Tk):
    """
    Représente quizzen classe app dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """

    def __init__(self) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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
        """
        Efface window et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

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
        """
        Effectue le traitement correspondant à center window dans le contexte de cette fenêtre.
        
        Paramètres :
            width : donnée nécessaire au traitement de « width ».
            height : donnée nécessaire au traitement de « height ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
        """
        Affiche login et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(700, 500)
        LoginWindow(self)

    def show_dashboard(self) -> None:
        """
        Affiche dashboard et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(800, 580)
        DashboardWindow(self)

    def show_eleves(self) -> None:
        """
        Affiche eleves et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(1300, 850)
        ElevesWindow(self)

    def show_cours(self) -> None:
        """
        Affiche cours et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(1000, 700)
        CoursWindow(self)

    def show_questionnaires(self) -> None:
        """
        Affiche questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(1000, 700)
        QuestionnairesWindow(self)

    def show_session(self) -> None:
        """
        Affiche session et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(1000, 700)
        SessionWindow(self)

    def show_statistiques(self) -> None:
        """
        Affiche statistiques et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.clear_window()
        self.center_window(1000, 700)
        StatistiquesWindow(self)

    def close_application(self) -> None:
        """
        Effectue le traitement correspondant à close application dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.quit()
        self.destroy()

    def logout(self) -> None:
        """
        Effectue le traitement correspondant à logout dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """

        self.current_user = {}
        self.api_client.token = None
        self.show_login()



def main() -> None:
    """
    Effectue le traitement correspondant à main dans le contexte de cette fenêtre.
    
    Retour :
        Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """
    application = QuizzenClasseApp()
    application.mainloop()


if __name__ == "__main__":
    main()

