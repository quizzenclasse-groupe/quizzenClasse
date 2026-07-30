# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Interface d'inscription et d'authentification de l'enseignant.

"""Fenêtre de connexion et d'inscription de l'enseignant.

Deux classes ici plutôt qu'un seul fichier séparé pour l'inscription :
``LoginWindow`` (l'écran principal, avec le formulaire connexion) et
``RegistrationWindow`` (la fenêtre modale "Créer un compte" ouverte
par-dessus). Elles sont regroupées parce que la seconde n'a de sens que
depuis la première et lui renvoie directement les identifiants créés.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from config import USE_API
from gui.common.messages import run_api_action


class LoginWindow(ttk.Frame):
    """Écran de connexion affiché au démarrage de l'application.

    Si ``USE_API`` est désactivé dans ``config.py`` (mode local sans
    serveur), la connexion est sautée automatiquement via
    ``_open_local_session`` : aucun identifiant n'est demandé.
    """

    def __init__(self, parent: tk.Tk) -> None:
        """Construit le formulaire de connexion et bascule directement au tableau de bord en mode local.

        Paramètres :
            parent : fenêtre racine de l'application (``tk.Tk``), qui
                porte ``api_client``, ``current_user`` et ``show_dashboard``.
        """
        super().__init__(parent, padding=40)
        self.parent = parent
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._create_content()
        # Entrée = validation du formulaire, comme un clic sur « Se connecter ».
        self.parent.bind("<Return>", self.login)

        if not USE_API:
            self.after(100, self._open_local_session)

    def _create_content(self) -> None:
        """Construit le formulaire de connexion (nom d'utilisateur, mot de passe) et ses boutons."""
        content = ttk.Frame(self, padding=30)
        content.grid(row=0, column=0)

        ttk.Label(content, text="QuizzenClasse", font=("Arial", 28, "bold")).pack(pady=(0, 8))
        ttk.Label(content, text="Connexion enseignant").pack(pady=(0, 25))

        form = ttk.LabelFrame(content, text="Identifiants", padding=20)
        form.pack(fill="x")

        ttk.Label(form, text="Nom d'utilisateur :").grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.username_entry = ttk.Entry(form, textvariable=self.username_var, width=32)
        self.username_entry.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form, text="Mot de passe :").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(form, textvariable=self.password_var, show="*", width=32).grid(row=1, column=1, padx=5, pady=8)

        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=2, pady=(14, 2))
        ttk.Button(buttons, text="Se connecter", command=self.login).pack(side="left", padx=4)
        ttk.Button(buttons, text="Créer un compte", command=self.open_registration).pack(side="left", padx=4)
        self.username_entry.focus_set()

    def _open_local_session(self) -> None:
        """Ouvre directement le tableau de bord en mode local (sans API), avec un profil de démonstration."""
        self.parent.current_user = self.parent.api_client.get_profile()
        self.parent.unbind("<Return>")
        self.parent.show_dashboard()

    def login(self, _event=None) -> None:
        """
        Vérifie les informations saisies, demande l'authentification de l'utilisateur et ouvre le tableau de bord en cas de réussite.

        Paramètres :
            _event : événement Tkinter ayant déclenché l'appel (touche
                Entrée ou clic sur le bouton).
        """
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showwarning("Identifiants incomplets", "Saisissez le nom d'utilisateur et le mot de passe.")
            return

        run_api_action(lambda: self.parent.api_client.login(username, password))
        if self.parent.api_client.token is None:
            return

        profile = run_api_action(self.parent.api_client.get_profile)
        if profile is None:
            self.parent.api_client.token = None
            return

        self.parent.current_user = {
            "id": profile["id"],
            "nom": profile.get("nom") or profile["nom_utilisateur"],
            "prenom": profile.get("prenom") or "",
            "etablissement": profile.get("nom_etablissement") or "Non renseigné",
            "nom_utilisateur": profile["nom_utilisateur"],
        }
        self.parent.unbind("<Return>")
        self.parent.show_dashboard()

    def open_registration(self) -> None:
        """Ouvre la fenêtre modale de création de compte."""
        RegistrationWindow(self.parent, self)


class RegistrationWindow(tk.Toplevel):
    """Fenêtre modale de création d'un compte enseignant.

    À l'inscription réussie, recopie automatiquement les identifiants
    saisis dans le formulaire de connexion sous-jacent (``login_window``),
    pour que l'utilisateur n'ait plus qu'à cliquer sur « Se connecter ».
    """

    def __init__(self, parent, login_window: LoginWindow) -> None:
        """Construit le formulaire d'inscription (identifiants + informations facultatives).

        Paramètres :
            parent : fenêtre racine de l'application (porte ``api_client``).
            login_window : écran de connexion à préremplir après une
                inscription réussie.
        """
        super().__init__(parent)
        self.parent = parent
        self.login_window = login_window
        self.title("Créer un compte enseignant")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.vars = {key: tk.StringVar() for key in (
            "nom_utilisateur", "mot_de_passe", "confirmation", "nom", "prenom", "email", "nom_etablissement"
        )}
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        fields = (
            ("Nom d'utilisateur * :", "nom_utilisateur", False),
            ("Mot de passe * :", "mot_de_passe", True),
            ("Confirmation * :", "confirmation", True),
            ("Nom :", "nom", False),
            ("Prénom :", "prenom", False),
            ("E-mail :", "email", False),
            ("Établissement :", "nom_etablissement", False),
        )
        for row, (label, key, secret) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=5)
            ttk.Entry(frame, textvariable=self.vars[key], show="*" if secret else "", width=34).grid(
                row=row, column=1, padx=8, pady=5
            )
        ttk.Button(frame, text="Créer le compte", command=self.register).grid(
            row=len(fields), column=0, columnspan=2, pady=(12, 0)
        )

    def register(self) -> None:
        """
        Valide le formulaire d'inscription puis transmet les informations nécessaires à la création d'un compte enseignant.

        Vérifie la longueur minimale du nom d'utilisateur et du mot de
        passe, ainsi que la correspondance des deux champs de mot de passe,
        avant l'appel à l'API.
        """
        username = self.vars["nom_utilisateur"].get().strip()
        password = self.vars["mot_de_passe"].get()
        if len(username) < 3:
            messagebox.showwarning("Inscription", "Le nom d'utilisateur doit contenir au moins 3 caractères.", parent=self)
            return
        if len(password) < 8:
            messagebox.showwarning("Inscription", "Le mot de passe doit contenir au moins 8 caractères.", parent=self)
            return
        if password != self.vars["confirmation"].get():
            messagebox.showwarning("Inscription", "Les mots de passe ne correspondent pas.", parent=self)
            return

        data = {"nom_utilisateur": username, "mot_de_passe": password}
        for key in ("nom", "prenom", "email", "nom_etablissement"):
            value = self.vars[key].get().strip()
            data[key] = value or None

        result = run_api_action(lambda: self.parent.api_client.register(data))
        if result is None:
            return
        self.login_window.username_var.set(username)
        self.login_window.password_var.set(password)
        messagebox.showinfo("Inscription", "Compte créé. Vous pouvez maintenant vous connecter.", parent=self)
        self.destroy()
