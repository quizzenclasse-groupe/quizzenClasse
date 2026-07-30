# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion commune des opérations et des messages affichés à l'utilisateur.

"""Fonctions communes pour exécuter une opération et afficher les erreurs de manière uniforme."""

from tkinter import messagebox

from client.client import ApiError


def run_api_action(action, on_success=None):
    """Exécute un appel API en centralisant la gestion des erreurs pour toute la GUI.

    C'est le point de passage unique de tous les appels réseau de
    l'application : chaque écran l'utilise pour appeler l'API sans avoir à
    répéter son propre bloc ``try/except``. En cas d'``ApiError`` (erreur
    HTTP ou réseau remontée par ``client.client``), un message d'erreur est
    affiché à l'utilisateur et la fonction renvoie ``None`` — c'est ce
    ``None`` que les écrans appelants utilisent pour interrompre leur
    traitement (annuler un rafraîchissement, ne pas fermer une fenêtre, etc.).

    Paramètres :
        action : fonction sans argument à exécuter (typiquement une
            ``lambda`` encapsulant un appel au client API).
        on_success : fonction optionnelle appelée avec le résultat si
            l'appel réussit, avant que ce résultat soit renvoyé.

    Retour :
        Le résultat de ``action()`` en cas de succès, ou ``None`` si une
        ``ApiError`` a été levée.
    """
    try:
        result = action()
        if on_success:
            on_success(result)
        return result
    except ApiError as error:
        messagebox.showerror("Erreur de communication", str(error))
        return None
