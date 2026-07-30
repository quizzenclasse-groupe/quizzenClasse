# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Widget Tkinter réutilisable (cadre défilant verticalement).

"""Cadre défilant vertical partagé par les fenêtres du module sessions.

``VerticalScrolledFrame`` encapsule un ``Canvas`` et une ``Scrollbar`` pour
permettre à un contenu plus haut que l'écran (le questionnaire complet
pendant une session, la liste des participations) de défiler proprement,
avec prise en charge de la molette sous Windows et sous Linux.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class VerticalScrolledFrame(ttk.Frame):
    """Cadre Tkinter défilant verticalement.

    Le contenu réel doit être ajouté comme enfant de ``self.content`` (et non
    de l'instance elle-même) : c'est ce cadre interne qui défile dans le
    ``Canvas``.
    """

    def __init__(self, parent, **kwargs) -> None:
        """Construit le canvas, la scrollbar et le cadre interne défilant.

        Le cadre interne (``self.content``) est celui dans lequel les
        fenêtres appelantes doivent placer leurs widgets.
        """
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # La zone de défilement doit être recalculée à chaque fois que le
        # contenu change de taille (ajout/suppression de widgets).
        self.content.bind("<Configure>", self._update_scrollregion)
        # Le cadre interne doit toujours occuper toute la largeur du canvas,
        # même quand la fenêtre est redimensionnée.
        self.canvas.bind("<Configure>", self._resize_content)
        # La molette n'est active que lorsque la souris survole ce widget,
        # pour ne pas capter le défilement d'autres zones de l'écran.
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _update_scrollregion(self, _event=None) -> None:
        """Recalcule la zone défilable du canvas d'après la taille réelle du contenu."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event) -> None:
        """Aligne la largeur du cadre interne sur celle du canvas parent."""
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event=None) -> None:
        """Active le défilement à la molette pendant que la souris est sur le cadre."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event=None) -> None:
        """Désactive le défilement à la molette dès que la souris quitte le cadre."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event) -> None:
        """Fait défiler le contenu sous Windows/macOS (delta multiple de 120)."""
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_mousewheel_linux(self, event):
        """Fait défiler le contenu avec la molette sous Linux.

        Le contrôle d'existence évite d'utiliser le canvas lorsque la fenêtre
        qui le contient vient d'être fermée.
        """
        try:
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
        except tk.TclError:
            # La fenêtre peut être détruite entre le contrôle et le défilement.
            return
