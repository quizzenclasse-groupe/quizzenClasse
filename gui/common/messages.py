# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion commune des opérations et des messages affichés à l’utilisateur.

"""Fonctions communes pour exécuter une opération et afficher les erreurs de manière uniforme."""

from tkinter import messagebox

from client.client import ApiError


def run_api_action(action, on_success=None):
    """
    Effectue le traitement correspondant à run api action dans le contexte de cette fenêtre.
    
    Paramètres :
        action : donnée nécessaire au traitement de « action ».
        on_success : donnée nécessaire au traitement de « on success ».
    
    Retour :
        Données calculées ou récupérées par la méthode.
    
    Traitement :
        Les contrôles de saisie et les erreurs attendues sont pris en compte avant
        d'actualiser les widgets concernés ou de poursuivre la navigation.
    """

    # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
    try:
        result = action()
        if on_success:
            on_success(result)
        return result
    except ApiError as error:
        messagebox.showerror("Erreur de communication", str(error))
        return None
