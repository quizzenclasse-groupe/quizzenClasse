# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Interface d'inscription et d'authentification de l'enseignant.

"""Fenêtre de connexion et d'inscription de l'enseignant."""

import tkinter as tk
from tkinter import messagebox, ttk

from config import USE_API
from gui.common.messages import run_api_action


class LoginWindow(ttk.Frame):
    """
    Représente login window dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent: tk.Tk) -> None:
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
        super().__init__(parent, padding=40)
        self.parent = parent
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._create_content()
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.parent.bind("<Return>", self.login)

        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        if not USE_API:
            self.after(100, self._open_local_session)

    def _create_content(self) -> None:
        """
        Effectue le traitement correspondant à create content dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
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
        """
        Effectue le traitement correspondant à open local session dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        self.parent.current_user = self.parent.api_client.get_profile()
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.parent.unbind("<Return>")
        self.parent.show_dashboard()

    def login(self, _event=None) -> None:
        """
        Vérifie les informations saisies, demande l'authentification de l'utilisateur et ouvre le tableau de bord en cas de réussite.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if not username or not password:
            messagebox.showwarning("Identifiants incomplets", "Saisissez le nom d'utilisateur et le mot de passe.")
            return

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
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
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.parent.unbind("<Return>")
        self.parent.show_dashboard()

    def open_registration(self) -> None:
        """
        Ouvre registration et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        RegistrationWindow(self.parent, self)


class RegistrationWindow(tk.Toplevel):
    """
    Représente registration window dans l'interface graphique QuizzenClasse.
    
    La classe rassemble les widgets de cet écran, les variables Tkinter associées
    et les méthodes déclenchées par les actions de l'utilisateur.
    """
    def __init__(self, parent, login_window: LoginWindow) -> None:
        """
        Initialise l'objet et prépare les données ainsi que les widgets nécessaires à son fonctionnement.
        
        Paramètres :
            parent : widget parent qui contient le composant.
            login_window : donnée nécessaire au traitement de « login window ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
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
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        username = self.vars["nom_utilisateur"].get().strip()
        password = self.vars["mot_de_passe"].get()
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if len(username) < 3:
            messagebox.showwarning("Inscription", "Le nom d'utilisateur doit contenir au moins 3 caractères.", parent=self)
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if len(password) < 8:
            messagebox.showwarning("Inscription", "Le mot de passe doit contenir au moins 8 caractères.", parent=self)
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if password != self.vars["confirmation"].get():
            messagebox.showwarning("Inscription", "Les mots de passe ne correspondent pas.", parent=self)
            return

        data = {"nom_utilisateur": username, "mot_de_passe": password}
        for key in ("nom", "prenom", "email", "nom_etablissement"):
            value = self.vars[key].get().strip()
            data[key] = value or None

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        result = run_api_action(lambda: self.parent.api_client.register(data))
        if result is None:
            return
        self.login_window.username_var.set(username)
        self.login_window.password_var.set(password)
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Inscription", "Compte créé. Vous pouvez maintenant vous connecter.", parent=self)
        self.destroy()
