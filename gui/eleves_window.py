# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Fichier de compatibilité réexportant la fenêtre graphique du module.

"""
Fichier de compatibilité.

Le véritable module se trouve maintenant dans ``gui/eleves``.
Grâce à ce relais, l'import existant dans ``main.py`` peut rester inchangé :

    from gui.eleves_window import ElevesWindow
"""

from gui.eleves.eleves_window import ElevesWindow

__all__ = ["ElevesWindow"]
