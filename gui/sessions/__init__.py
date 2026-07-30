# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Déclaration du paquet Python et exposition de ses composants publics.

"""Module de gestion des sessions de quiz.

Découpé en plusieurs fichiers par responsabilité :
- ``widgets`` : composants Tkinter réutilisables (cadre défilant).
- ``participation_window`` : inscription et évaluation des participations.
- ``session_player`` : déroulement d'une session (lecteur de quiz).
- ``session_window`` : création et suivi des sessions (fenêtre principale).
"""

from .session_window import SessionWindow
from .session_player import SessionPlayerWindow
from .participation_window import ParticipationWindow
from .widgets import VerticalScrolledFrame

__all__ = [
    "SessionWindow",
    "SessionPlayerWindow",
    "ParticipationWindow",
    "VerticalScrolledFrame",
]
