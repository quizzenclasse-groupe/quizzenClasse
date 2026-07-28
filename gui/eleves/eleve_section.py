# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Gestion graphique des élèves rattachés à un niveau.

"""Section graphique chargée de la gestion des élèves via l'API."""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from gui.common.messages import run_api_action
from utils.validators import clean_text, validate_date, validate_person_name, validate_postal_code, validate_required_text
from .widgets import create_labeled_entry


class EleveSection(ttk.Frame):
    """
    Représente eleve section dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent, api, on_niveau_changed: Callable[[int], None]) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            api : client de communication utilisé par la fenêtre.
            on_niveau_changed : donnée nécessaire au traitement de « on niveau changed ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        super().__init__(parent, padding=10)
        self.api = api
        self.on_niveau_changed_callback = on_niveau_changed
        self.selected_eleve_id: Optional[int] = None
        self.current_niveau_id: Optional[int] = None
        self.niveau_combobox_ids: dict[str, int] = {}
        self.eleves_by_id: dict[int, dict] = {}
        self.selected_eleve_niveau_ids: list[int] = []

        self.nom_eleve_var = tk.StringVar()
        self.prenom_var = tk.StringVar()
        self.date_naissance_var = tk.StringVar()
        self.redoublant_var = tk.BooleanVar(value=False)
        self.ville_var = tk.StringVar()
        self.cp_var = tk.StringVar()
        self.niveau_var = tk.StringVar()
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
        form = ttk.LabelFrame(self, text="Informations de l'élève", padding=10)
        form.pack(fill="x")
        create_labeled_entry(form, "Nom :", self.nom_eleve_var, 0)
        create_labeled_entry(form, "Prénom :", self.prenom_var, 1)
        create_labeled_entry(form, "Date de naissance :", self.date_naissance_var, 2)
        ttk.Label(form, text="Format : JJ/MM/AAAA").grid(row=2, column=2, padx=5, sticky="w")
        create_labeled_entry(form, "Ville :", self.ville_var, 3)
        create_labeled_entry(form, "Code postal :", self.cp_var, 4)
        ttk.Label(form, text="Niveau :").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.niveau_combobox = ttk.Combobox(form, textvariable=self.niveau_var, state="readonly", width=30)
        self.niveau_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        ttk.Checkbutton(form, text="Élève redoublant", variable=self.redoublant_var).grid(
            row=6, column=1, padx=5, pady=5, sticky="w"
        )
        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        ttk.Button(buttons, text="Ajouter", command=self.add_eleve).pack(side="left", padx=3)
        ttk.Button(buttons, text="Modifier", command=self.update_eleve).pack(side="left", padx=3)
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
        frame = ttk.LabelFrame(self, text="Élèves du niveau sélectionné", padding=5)
        frame.pack(fill="both", expand=True, pady=(15, 0))
        self.tree = ttk.Treeview(frame, columns=("nom", "prenom", "date", "ville", "cp", "redoublant"), show="headings", height=15)
        for name, title, width in (
            ("nom", "Nom", 120), ("prenom", "Prénom", 120), ("date", "Date de naissance", 130),
            ("ville", "Ville", 120), ("cp", "Code postal", 90), ("redoublant", "Redoublant", 90)
        ):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width)
        vertical = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.tree.bind("<<TreeviewSelect>>", self._handle_selection)

    @staticmethod
    def _to_api_date(value: str):
        """
        Effectue le traitement correspondant à to api date dans le contexte de cette fenêtre.
        
        Paramètres :
            value : donnée nécessaire au traitement de « value ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        value = value.strip()
        if not value:
            return None
        return datetime.strptime(value, "%d/%m/%Y").date().isoformat()

    @staticmethod
    def _to_display_date(value):
        """
        Effectue le traitement correspondant à to display date dans le contexte de cette fenêtre.
        
        Paramètres :
            value : donnée nécessaire au traitement de « value ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if not value:
            return ""
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")

    def _validate_form(self):
        """
        Effectue le traitement correspondant à validate form dans le contexte de cette fenêtre.
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        for variable, label in ((self.nom_eleve_var, "Nom"), (self.prenom_var, "Prénom")):
            valid, message = validate_person_name(variable.get(), label)
            if not valid:
                messagebox.showerror("Données invalides", message)
                return None
        valid, message = validate_date(self.date_naissance_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return None
        valid, message = validate_required_text(self.ville_var.get(), "Ville")
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return None
        valid, message = validate_postal_code(self.cp_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not valid:
            messagebox.showerror("Données invalides", message)
            return None
        niveau_id = self.niveau_combobox_ids.get(self.niveau_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if niveau_id is None:
            messagebox.showerror("Niveau obligatoire", "Sélectionnez un niveau pour l'élève.")
            return None
        return {
            "nom": clean_text(self.nom_eleve_var.get()),
            "prenom": clean_text(self.prenom_var.get()),
            "date_naissance": self._to_api_date(self.date_naissance_var.get()),
            "redoublant": self.redoublant_var.get(),
            "ville": clean_text(self.ville_var.get()),
            "cp": clean_text(self.cp_var.get()),
            "niveau_ids": [niveau_id],
        }

    def add_eleve(self) -> None:
        """
        Ajoute eleve et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        data = self._validate_form()
        if data is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.create_eleve(data))
        if result is None:
            return
        niveau_id = data["niveau_ids"][0]
        self.clear_form(preserve_niveau=True)
        self.on_niveau_changed_callback(niveau_id)
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Ajout réussi", "L'élève a été ajouté.")

    def update_eleve(self) -> None:
        """
        Met à jour eleve et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_eleve_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un élève à modifier.")
            return
        data = self._validate_form()
        if data is None:
            return
        niveau_id = data.pop("niveau_ids")[0]
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if self.selected_eleve_niveau_ids and niveau_id not in self.selected_eleve_niveau_ids:
            messagebox.showwarning(
                "Changement de niveau non disponible",
                "Les informations de l'élève peuvent être modifiées, mais son changement de niveau n'est pas disponible.",
            )
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.api.update_eleve(self.selected_eleve_id, data))
        if result is None:
            return
        self.clear_form(preserve_niveau=True)
        self.on_niveau_changed_callback(niveau_id)
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Modification réussie", "Les informations de l'élève ont été modifiées.")

    def set_current_niveau(self, niveau_id: Optional[int]) -> None:
        """
        Effectue le traitement correspondant à set current niveau dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.current_niveau_id = niveau_id
        self.refresh_niveaux(niveau_id)
        self.clear_form(preserve_niveau=True)
        self.refresh_eleves()

    def refresh_niveaux(self, niveau_to_select: Optional[int] = None) -> None:
        """
        Actualise niveaux et synchronise l'affichage avec le résultat obtenu.
        
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
        self.niveau_combobox_ids = {item["nom_niveau"]: item["id"] for item in niveaux}
        self.niveau_combobox["values"] = list(self.niveau_combobox_ids)
        if niveau_to_select is None:
            self.niveau_var.set("")
        else:
            self._select_niveau_in_combobox(niveau_to_select)

    def refresh_eleves(self) -> None:
        """
        Actualise eleves et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())
        self.eleves_by_id = {}
        if self.current_niveau_id is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        eleves = run_api_action(lambda: self.api.list_eleves(self.current_niveau_id))
        if eleves is None:
            return
        self.eleves_by_id = {item["id"]: item for item in eleves}
        # Met à jour le contenu du tableau affiché dans l'interface.
        for eleve in eleves:
            self.tree.insert("", "end", iid=str(eleve["id"]), values=(
                eleve.get("nom_eleve") or "", eleve.get("prenom") or "", self._to_display_date(eleve.get("date_naissance")),
                eleve.get("ville") or "", eleve.get("cp") or "", "Oui" if eleve.get("redoublant") else "Non"
            ))

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
        if not selection:
            return
        eleve = self.eleves_by_id.get(int(selection[0]))
        if eleve is None:
            return
        self.selected_eleve_id = eleve["id"]
        self.nom_eleve_var.set(eleve.get("nom_eleve") or "")
        self.prenom_var.set(eleve.get("prenom") or "")
        self.date_naissance_var.set(self._to_display_date(eleve.get("date_naissance")))
        self.redoublant_var.set(bool(eleve.get("redoublant")))
        self.ville_var.set(eleve.get("ville") or "")
        self.cp_var.set(eleve.get("cp") or "")
        niveau_ids = eleve.get("niveau_ids") or []
        self.selected_eleve_niveau_ids = list(niveau_ids)
        if niveau_ids:
            self._select_niveau_in_combobox(niveau_ids[0])

    def _select_niveau_in_combobox(self, niveau_id: int) -> None:
        """
        Effectue le traitement correspondant à select niveau in combobox dans le contexte de cette fenêtre.
        
        Paramètres :
            niveau_id : identifiant du niveau concerné.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        for display_name, stored_id in self.niveau_combobox_ids.items():
            if stored_id == niveau_id:
                self.niveau_var.set(display_name)
                return
        self.niveau_var.set("")

    def clear_form(self, preserve_niveau: bool = False) -> None:
        """
        Efface form et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            preserve_niveau : donnée nécessaire au traitement de « preserve niveau ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.selected_eleve_id = None
        self.selected_eleve_niveau_ids = []
        self.nom_eleve_var.set("")
        self.prenom_var.set("")
        self.date_naissance_var.set("")
        self.redoublant_var.set(False)
        self.ville_var.set("")
        self.cp_var.set("")
        if not preserve_niveau:
            self.niveau_var.set("")
