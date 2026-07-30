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
    """Panneau de gauche de l'écran élèves : liste et formulaire des niveaux (classes) de l'enseignant.

    Un niveau est rattaché à un établissement, choisi via un champ de
    recherche à la volée (``_search_etablissements``) car la liste des
    établissements vient d'une table nationale bien trop grande pour un
    simple menu déroulant.

    Cette section ne connaît pas ``EleveSection`` : elle ne fait que
    notifier ``on_niveau_selected`` à chaque changement de niveau
    sélectionné (clic dans le tableau, ajout, suppression). C'est
    ``ElevesWindow`` qui relie les deux entre elles pour recharger la
    liste des élèves du niveau correspondant.
    """

    def __init__(self, parent, api, on_niveau_selected: Callable[[Optional[int]], None]) -> None:
        """Initialise l'état de la section et construit le formulaire puis le tableau.

        Paramètres :
            parent : widget parent qui contient cette section.
            api : client HTTP utilisé pour tous les appels à l'API REST.
            on_niveau_selected : fonction rappelée avec l'identifiant du
                niveau sélectionné (ou ``None`` s'il n'y en a plus), pour
                synchroniser la liste des élèves affichée à côté.
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
        """Construit le formulaire : nom du niveau, recherche d'établissement, boutons CRUD."""
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
        # Recherche différée (300 ms) à chaque frappe, pour éviter un appel API par caractère tapé.
        self.etablissement_combo.bind("<KeyRelease>", self._schedule_etablissement_search)
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
        """Construit le tableau listant les niveaux déjà enregistrés (nom, effectif, établissement)."""
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
        self.tree.bind("<<TreeviewSelect>>", self._handle_selection)

    def _schedule_etablissement_search(self, _event=None) -> None:
        """Reporte la recherche d'établissement de 300 ms après chaque frappe (anti-rebond).

        Annule la recherche précédemment planifiée si l'utilisateur continue
        de taper, pour ne lancer qu'un seul appel API par pause de saisie.
        """
        if self._search_job is not None:
            try:
                self.after_cancel(self._search_job)
            except tk.TclError:
                pass
        self._search_job = self.after(300, self._search_etablissements)

    def _search_etablissements(self) -> None:
        """Recherche les établissements correspondant au texte saisi (à partir de 2 caractères).

        Les résultats sont mis en cache dans ``etablissement_names_by_id``,
        partagé avec le client API pour que d'autres écrans (participations,
        sessions) réutilisent les noms déjà résolus sans nouvel appel.
        """
        self._search_job = None
        query = clean_text(self.etablissement_var.get())
        if len(query) < 2:
            self.etablissement_combo["values"] = ()
            self.etablissement_ids.clear()
            self.selected_etablissement_id = None
            return
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
        """Mémorise l'identifiant de l'établissement choisi dans la liste déroulante."""
        self.selected_etablissement_id = self.etablissement_ids.get(self.etablissement_var.get())

    def _find_etablissement(self, name: str):
        """Recherche un établissement par son nom exact (repli sur le premier résultat approché).

        Utilisé quand l'utilisateur valide le formulaire sans avoir cliqué
        sur une suggestion de la liste déroulante.
        """
        results = run_api_action(lambda: self.api.search_etablissements(name))
        if not results:
            messagebox.showerror("Établissement introuvable", "Aucun établissement ne correspond à ce nom.")
            return None
        lowered = name.casefold()
        exact = next((item for item in results if item["nom_etablissement"].casefold() == lowered), None)
        return exact or results[0]

    def add_niveau(self) -> None:
        """Valide le formulaire puis crée un niveau, en résolvant l'établissement si besoin."""
        valid, message = validate_required_text(self.nom_niveau_var.get(), "Nom du niveau")
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        valid, message = validate_required_text(self.etablissement_var.get(), "Établissement")
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        etablissement_id = self.etablissement_ids.get(self.etablissement_var.get())
        if etablissement_id is None:
            # L'utilisateur a tapé un nom sans cliquer sur une suggestion : on le résout ici.
            etablissement = self._find_etablissement(clean_text(self.etablissement_var.get()))
            if etablissement is None:
                return
            etablissement_id = etablissement["id"]
            self.etablissement_names_by_id[etablissement_id] = etablissement["nom_etablissement"]
            if hasattr(self.api, "etablissement_names_by_id"):
                self.api.etablissement_names_by_id[etablissement_id] = etablissement["nom_etablissement"]
        result = run_api_action(lambda: self.api.create_niveau({
            "nom_niveau": clean_text(self.nom_niveau_var.get()),
            "etablissement_id": etablissement_id,
        }))
        if result is None:
            return
        self.clear_form()
        self.refresh(result["id"])
        messagebox.showinfo("Ajout réussi", "Le niveau a été ajouté.")

    def update_niveau(self) -> None:
        """Renomme le niveau sélectionné (l'établissement associé n'est pas modifiable ici)."""
        if self.selected_niveau_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un niveau à modifier.")
            return
        valid, message = validate_required_text(self.nom_niveau_var.get(), "Nom du niveau")
        if not valid:
            messagebox.showerror("Données invalides", message)
            return
        result = run_api_action(lambda: self.api.update_niveau(
            self.selected_niveau_id, {"nom_niveau": clean_text(self.nom_niveau_var.get())}
        ))
        if result is None:
            return
        self.refresh(self.selected_niveau_id)
        messagebox.showinfo("Modification réussie", "Le nom du niveau a été modifié.")

    def delete_niveau(self) -> None:
        """Supprime le niveau sélectionné après confirmation de l'utilisateur."""
        if self.selected_niveau_id is None:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un niveau à supprimer.")
            return
        if not messagebox.askyesno("Confirmer la suppression", "Voulez-vous supprimer ce niveau ?"):
            return
        run_api_action(lambda: self.api.delete_niveau(self.selected_niveau_id))
        self.selected_niveau_id = None
        self.clear_form()
        self.refresh()
        self.on_niveau_selected_callback(None)

    def refresh(self, niveau_to_select: Optional[int] = None) -> None:
        """Recharge la liste des niveaux depuis l'API et repeuple le tableau.

        Paramètres :
            niveau_to_select : si fourni, sélectionne ce niveau après le
                rechargement (utilisé après un ajout ou une modification).
        """
        niveaux = run_api_action(self.api.list_niveaux)
        if niveaux is None:
            return
        self.niveaux_by_id = {item["id"]: item for item in niveaux}
        self.tree.delete(*self.tree.get_children())
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
        """Sélectionne et met en évidence un niveau donné dans le tableau, puis charge son formulaire."""
        item_id = str(niveau_id)
        if self.tree.exists(item_id):
            self.tree.selection_set(item_id)
            self.tree.focus(item_id)
            self.tree.see(item_id)
            self._load_selected_niveau(niveau_id)

    def _handle_selection(self, _event=None) -> None:
        """Réagit à un clic sur une ligne du tableau en chargeant le niveau correspondant."""
        selection = self.tree.selection()
        if selection:
            self._load_selected_niveau(int(selection[0]))

    def _load_selected_niveau(self, niveau_id: int) -> None:
        """Recopie les données du niveau sélectionné dans le formulaire et notifie le callback parent."""
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
        """Vide les champs du formulaire de saisie d'un niveau."""
        self.nom_niveau_var.set("")
        self.etablissement_var.set("")
        self.selected_etablissement_id = None
