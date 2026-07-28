# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion des cours ; écran non affiché dans le tableau de bord actuel.

"""Gestion des cours via les routes CRUD déjà fournies par l'API."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from gui.common.messages import run_api_action
from gui.common.page import create_page_header


class CoursWindow(ttk.Frame):
    """
    Représente cours window dans l'interface graphique QuizzenClasse.
    
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
        super().__init__(parent, padding=18)
        self.parent = parent
        self.api = parent.api_client
        self.selected_id: int | None = None
        self.cours_by_id: dict[int, dict] = {}
        self.nom_var = tk.StringVar()
        self.pack(fill="both", expand=True)
        create_page_header(self, "Gestion des cours", parent.show_dashboard)
        self._create_widgets()
        self.refresh()

    def _create_widgets(self) -> None:
        """
        Effectue le traitement correspondant à create widgets dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        form = ttk.LabelFrame(self, text="Cours", padding=12)
        form.pack(fill="x", pady=(10, 8))
        ttk.Label(form, text="Nom du cours * :").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.nom_var).grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        ttk.Label(form, text="Description :").grid(row=1, column=0, sticky="nw", pady=4)
        self.description_text = tk.Text(form, height=5, wrap="word")
        self.description_text.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Créer", command=self.create).pack(side="left", padx=3)
        ttk.Button(actions, text="Modifier", command=self.update).pack(side="left", padx=3)
        ttk.Button(actions, text="Supprimer", command=self.delete).pack(side="left", padx=3)
        ttk.Button(actions, text="Nouveau", command=self.clear).pack(side="left", padx=3)
        ttk.Button(actions, text="Actualiser", command=self.refresh).pack(side="right", padx=3)

        frame = ttk.LabelFrame(self, text="Mes cours", padding=8)
        frame.pack(fill="both", expand=True)
        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(container, columns=("nom", "description"), show="headings", selectmode="browse")
        self.tree.heading("nom", text="Nom du cours")
        self.tree.heading("description", text="Description")
        self.tree.column("nom", width=220, minwidth=140)
        self.tree.column("description", width=600, minwidth=250)
        sy = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.tree.bind("<<TreeviewSelect>>", self._load_selected)

    def _payload(self) -> dict | None:
        """
        Effectue le traitement correspondant à payload dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        nom = self.nom_var.get().strip()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not nom:
            messagebox.showwarning("Nom obligatoire", "Saisissez le nom du cours.")
            return None
        description = self.description_text.get("1.0", "end").strip() or None
        return {"nom_cours": nom, "description": description}

    def create(self) -> None:
        """
        Effectue le traitement correspondant à create dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        payload = self._payload()
        if payload is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.create_cours(payload))
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if result is not None:
            self.clear(); self.refresh()
            messagebox.showinfo("Cours", "Cours créé.")

    def update(self) -> None:
        """
        Effectue le traitement correspondant à update dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_id is None:
            messagebox.showwarning("Sélection", "Sélectionnez un cours à modifier.")
            return
        payload = self._payload()
        if payload is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.update_cours(self.selected_id, payload))
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if result is not None:
            self.clear(); self.refresh()
            messagebox.showinfo("Cours", "Cours modifié.")

    def delete(self) -> None:
        """
        Effectue le traitement correspondant à delete dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_id is None:
            messagebox.showwarning("Sélection", "Sélectionnez un cours à supprimer.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not messagebox.askyesno("Confirmation", "Supprimer ce cours ?"):
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.delete_cours(self.selected_id))
        if result:
            self.clear(); self.refresh()

    def refresh(self) -> None:
        """
        Recharge les données affichées afin de présenter l'état le plus récent de l'application.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        items = run_api_action(self.api.list_cours)
        if items is None:
            return
        self.cours_by_id = {item["id"]: item for item in items}
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())
        # Met à jour le contenu du tableau affiché dans l'interface.
        for item in items:
            self.tree.insert("", "end", iid=str(item["id"]), values=(item.get("nom_cours", ""), item.get("description") or ""))

    def _load_selected(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à load selected dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        if not selection:
            return
        self.selected_id = int(selection[0])
        item = self.cours_by_id.get(self.selected_id, {})
        self.nom_var.set(item.get("nom_cours") or "")
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", item.get("description") or "")

    def clear(self) -> None:
        """
        Effectue le traitement correspondant à clear dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.selected_id = None
        self.nom_var.set("")
        self.description_text.delete("1.0", "end")
        self.tree.selection_remove(self.tree.selection())
