# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion graphique des niveaux et de leur établissement.

"""Section graphique chargée de la gestion des niveaux via l'API."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from gui.common.messages import run_api_action
from utils.validators import clean_text, validate_required_text
from .widgets import create_labeled_entry


class NiveauSection(ttk.Frame):
    """
    Représente niveau section dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent, api, on_niveau_selected: Callable[[Optional[int]], None]) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            api : client de communication utilisé par la fenêtre.
            on_niveau_selected : donnée nécessaire au traitement de « on niveau selected ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent, padding=10)
        self.api = api
        self.on_niveau_selected_callback = on_niveau_selected
        self.selected_niveau_id: Optional[int] = None
        self.selected_etablissement_id: Optional[int] = None
        self.niveaux_by_id: dict[int, dict] = {}
        self.etablissement_ids: dict[str, int] = {}
        self.etablissement_names_by_id: dict[int, str] = {}
        self._search_job: str | None = None

        self.nom_niveau_var = tk.StringVar()
        self.etablissement_var = tk.StringVar()
        self._create_form()
        self._create_table()

    def _create_form(self) -> None:
        """
        Effectue le traitement correspondant à create form dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        form = ttk.LabelFrame(self, text="Informations du niveau", padding=10)
        form.pack(fill="x")
        create_labeled_entry(form, "Nom du niveau :", self.nom_niveau_var, 0)
        ttk.Label(form, text="Établissement :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.etablissement_combo = ttk.Combobox(
            form,
            textvariable=self.etablissement_var,
            state="normal",
            width=42,
        )
        self.etablissement_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.etablissement_combo.bind("<KeyRelease>", self._schedule_etablissement_search)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.etablissement_combo.bind("<<ComboboxSelected>>", self._select_etablissement)
        ttk.Label(form, text="Tapez au moins 2 caractères puis choisissez un établissement dans la liste proposée.").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5
        )
        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        ttk.Button(buttons, text="Ajouter", command=self.add_niveau).pack(side="left", padx=3)
        ttk.Button(buttons, text="Modifier le nom", command=self.update_niveau).pack(side="left", padx=3)
        ttk.Button(buttons, text="Supprimer", command=self.delete_niveau).pack(side="left", padx=3)
        ttk.Button(buttons, text="Vider", command=self.clear_form).pack(side="left", padx=3)

    def _create_table(self) -> None:
        """
        Effectue le traitement correspondant à create table dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        frame = ttk.LabelFrame(self, text="Niveaux enregistrés", padding=5)
        frame.pack(fill="both", expand=True, pady=(15, 0))
        self.tree = ttk.Treeview(frame, columns=("nom", "effectif", "etablissement"), show="headings", height=15)
        for name, title, width in (
            ("nom", "Niveau", 150), ("effectif", "Effectif", 70), ("etablissement", "Établissement", 220)
        ):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.tree.bind("<<TreeviewSelect>>", self._handle_selection)

    def _schedule_etablissement_search(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à schedule etablissement search dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except tk.TclError:
                pass
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self._search_job = self.after(300, self._search_etablissements)

    def _search_etablissements(self) -> None:
        """
        Effectue le traitement correspondant à search etablissements dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self._search_job = None
        query = clean_text(self.etablissement_var.get())
        if len(query) < 2:
            self.etablissement_combo["values"] = ()
            self.etablissement_ids.clear()
            self.selected_etablissement_id = None
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        results = run_api_action(lambda: self.api.search_etablissements(query))
        if results is None:
            return
        self.etablissement_ids = {}
        labels = []
        for item in results:
            name = item.get("nom_etablissement") or f"Établissement {item['id']}"
            postal = item.get("code_postal") or ""
            department = item.get("nom_departement") or ""
            details = " — ".join(part for part in (postal, department) if part)
            label = f"{name} — {details}" if details else name
            labels.append(label)
            self.etablissement_ids[label] = item["id"]
            self.etablissement_names_by_id[item["id"]] = name
            if hasattr(self.api, "etablissement_names_by_id"):
                self.api.etablissement_names_by_id[item["id"]] = name
        self.etablissement_combo["values"] = labels
        if labels:
            self.etablissement_combo.event_generate("<Down>")

    def _select_etablissement(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à select etablissement dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.selected_etablissement_id = self.etablissement_ids.get(self.etablissement_var.get())

    def _find_etablissement(self, name: str):
        """
        Effectue le traitement correspondant à find etablissement dans le contexte de cette fenêtre.
        
        Paramètres :
            name : donnée nécessaire au traitement de « name ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        results = run_api_action(lambda: self.api.search_etablissements(name))
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not results:
            messagebox.showerror("Établissement introuvable", "Aucun établissement ne correspond à ce nom.")
            return None
        lowered = name.casefold()
        exact = next((item for item in results if item["nom_etablissement"].casefold() == lowered), None)
        return exact or results[0]

    def add_niveau(self) -> None:
        """
        Ajoute niveau et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        valid, message = validate_required_text(self.nom_niveau_var.get(), "Nom du niveau")
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        valid, message = validate_required_text(self.etablissement_var.get(), "Établissement")
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        etablissement_id = self.etablissement_ids.get(self.etablissement_var.get())
        if etablissement_id is None:
            etablissement = self._find_etablissement(clean_text(self.etablissement_var.get()))
            if etablissement is None:
                return
            etablissement_id = etablissement["id"]
            self.etablissement_names_by_id[etablissement_id] = etablissement["nom_etablissement"]
            if hasattr(self.api, "etablissement_names_by_id"):
                self.api.etablissement_names_by_id[etablissement_id] = etablissement["nom_etablissement"]
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.create_niveau({
            "nom_niveau": clean_text(self.nom_niveau_var.get()),
            "etablissement_id": etablissement_id,
        }))
        if result is None:
            return
        self.clear_form()
        self.refresh(result["id"])
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Ajout réussi", "Le niveau a été ajouté.")

    def update_niveau(self) -> None:
        """
        Met à jour niveau et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_niveau_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un niveau à modifier.")
            return
        valid, message = validate_required_text(self.nom_niveau_var.get(), "Nom du niveau")
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.update_niveau(
            self.selected_niveau_id, {"nom_niveau": clean_text(self.nom_niveau_var.get())}
        ))
        if result is None:
            return
        self.refresh(self.selected_niveau_id)
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Modification réussie", "Le nom du niveau a été modifié.")

    def delete_niveau(self) -> None:
        """
        Supprime niveau et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_niveau_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un niveau à supprimer.")
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not messagebox.askyesno("Confirmer la suppression", "Voulez-vous supprimer ce niveau ?"):
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        run_api_action(lambda: self.api.delete_niveau(self.selected_niveau_id))
        self.selected_niveau_id = None
        self.clear_form()
        self.refresh()
        self.on_niveau_selected_callback(None)

    def refresh(self, niveau_to_select: Optional[int] = None) -> None:
        """
        Recharge les données affichées afin de présenter l'état le plus récent de l'application.
        
        Paramètres :
            niveau_to_select : donnée nécessaire au traitement de « niveau to select ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        niveaux = run_api_action(self.api.list_niveaux)
        if niveaux is None:
            return
        self.niveaux_by_id = {item["id"]: item for item in niveaux}
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())
        # Met à jour le contenu du tableau affiché dans l'interface.
        for niveau in niveaux:
            etablissement_id = niveau["etablissement_id"]
            etablissement_display = self.etablissement_names_by_id.get(
                etablissement_id,
                f"ID {etablissement_id}",
            )
            self.tree.insert("", "end", iid=str(niveau["id"]), values=(
                niveau["nom_niveau"], niveau.get("effectif", 0), etablissement_display
            ))
        if niveau_to_select is not None:
            self.select_niveau(niveau_to_select)
        elif not niveaux:
            self.on_niveau_selected_callback(None)

    def select_niveau(self, niveau_id: int) -> None:
        """
        Sélectionne niveau et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        item_id = str(niveau_id)
        if self.tree.exists(item_id):
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
            self._load_selected_niveau(niveau_id)

    def _handle_selection(self, _event=None) -> None:
        """
        Effectue le traitement correspondant à handle selection dans le contexte de cette fenêtre.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        selection = self.tree.selection()
        if selection:
            self._load_selected_niveau(int(selection[0]))

    def _load_selected_niveau(self, niveau_id: int) -> None:
        """
        Effectue le traitement correspondant à load selected niveau dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        niveau = self.niveaux_by_id.get(niveau_id)
        if niveau is None:
            return
        self.selected_niveau_id = niveau_id
        self.nom_niveau_var.set(niveau["nom_niveau"])
        etablissement_id = niveau["etablissement_id"]
        self.selected_etablissement_id = etablissement_id
        self.etablissement_var.set(
            self.etablissement_names_by_id.get(etablissement_id, f"ID {etablissement_id}")
        )
        self.on_niveau_selected_callback(niveau_id)

    def clear_form(self) -> None:
        """
        Efface form et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.nom_niveau_var.set("")
        self.etablissement_var.set("")
        self.selected_etablissement_id = None
