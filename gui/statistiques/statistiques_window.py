# Auteur : Mbodji Rokhaya Fall
# Formation : L2 Informatique - IED, Université Paris 8
# Rôle du fichier : Consultation des statistiques, commentaires et rapports de session.

"""Consultation des statistiques et du détail des participations."""

from __future__ import annotations

import csv
import tkinter as tk
from textwrap import wrap
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.common.messages import run_api_action
from gui.common.page import create_page_header


class StatistiquesWindow(ttk.Frame):
    """
    Représente statistiques window dans l'interface graphique QuizzenClasse.
    
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

        self.questionnaire_ids: dict[str, int] = {}
        self.questionnaires_by_id: dict[int, dict] = {}
        self.session_ids: dict[str, int] = {}
        self.sessions_by_id: dict[int, dict] = {}
        self.participant_names: dict[tuple[str, int], str] = {}
        self.participations: list[dict] = []

        self.questionnaire_var = tk.StringVar()
        self.session_var = tk.StringVar()
        self.questionnaire_info_var = tk.StringVar(value="Questionnaire : —")
        self.session_info_var = tk.StringVar(value="Session : —")
        self.session_meta_var = tk.StringVar(value="Mode / statut : —")
        self.last_stats = None
        self.values = {
            key: tk.StringVar(value="—")
            for key in ("participants", "evalues", "moyenne", "minimum", "maximum", "reussite")
        }

        self.pack(fill="both", expand=True)
        create_page_header(self, "Statistiques et rapport", parent.show_dashboard)
        self._create_selection()
        self._create_result()
        self.load_questionnaires()

    def _create_selection(self) -> None:
        """
        Effectue le traitement correspondant à create selection dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        frame = ttk.LabelFrame(self, text="Choix de la session", padding=10)
        frame.pack(fill="x")

        ttk.Label(frame, text="Questionnaire :").grid(row=0, column=0, sticky="w")
        self.questionnaire_combo = ttk.Combobox(
            frame, textvariable=self.questionnaire_var, state="readonly"
        )
        self.questionnaire_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        # Associe le traitement à un événement Tkinter ou à une exécution différée.
        self.questionnaire_combo.bind("<<ComboboxSelected>>", self.load_sessions)

        ttk.Label(frame, text="Session :").grid(row=1, column=0, sticky="w")
        self.session_combo = ttk.Combobox(
            frame, textvariable=self.session_var, state="readonly"
        )
        self.session_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=2, pady=6)
        ttk.Button(actions, text="Calculer", command=self.load_statistics).pack(side="left", padx=4)
        ttk.Button(actions, text="Voir le rapport", command=self.show_report).pack(side="left", padx=4)
        ttk.Button(actions, text="Exporter CSV", command=self.export_csv).pack(side="left", padx=4)
        ttk.Button(actions, text="Afficher graphique", command=self.show_chart).pack(side="left", padx=4)
        frame.columnconfigure(1, weight=1)

    def _create_result(self) -> None:
        """
        Effectue le traitement correspondant à create result dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        result_frame = ttk.LabelFrame(self, text="Résultats", padding=12)
        result_frame.pack(fill="both", expand=True, pady=(12, 0))

        identity = ttk.Frame(result_frame)
        identity.pack(fill="x", pady=(0, 8))
        ttk.Label(identity, textvariable=self.questionnaire_info_var, font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Label(identity, textvariable=self.session_info_var, font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Label(identity, textvariable=self.session_meta_var).pack(anchor="w")

        indicators = ttk.LabelFrame(result_frame, text="Indicateurs globaux", padding=8)
        indicators.pack(fill="x")
        labels = (
            ("participants", "Nombre de participations"),
            ("evalues", "Participations évaluées"),
            ("moyenne", "Moyenne"),
            ("minimum", "Score minimum"),
            ("maximum", "Score maximum"),
            ("reussite", "Taux de réussite"),
        )
        for index, (key, label) in enumerate(labels):
            row, col = divmod(index, 3)
            box = ttk.Frame(indicators)
            box.grid(row=row, column=col, sticky="ew", padx=8, pady=5)
            ttk.Label(box, text=f"{label} :", font=("Arial", 10, "bold")).pack(anchor="w")
            ttk.Label(box, textvariable=self.values[key]).pack(anchor="w")
            indicators.columnconfigure(col, weight=1)

        details = ttk.LabelFrame(result_frame, text="Résultats et commentaires par participant", padding=8)
        details.pack(fill="both", expand=True, pady=(10, 0))

        tree_container = ttk.Frame(details)
        tree_container.pack(fill="both", expand=True)
        style = ttk.Style(self)
        style.configure("Statistics.Treeview", rowheight=54)
        self.tree = ttk.Treeview(
            tree_container,
            columns=("participant", "score", "commentaire_initial", "commentaire_final"),
            show="headings",
            height=9,
            style="Statistics.Treeview",
        )
        for name, title, width, anchor in (
            ("participant", "Élève / équipe", 245, "w"),
            ("score", "Score", 80, "center"),
            ("commentaire_initial", "Commentaire initial", 260, "w"),
            ("commentaire_final", "Commentaire final", 310, "w"),
        ):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width, minwidth=60, anchor=anchor)

        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

    def load_questionnaires(self) -> None:
        """
        Charge questionnaires et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        items = run_api_action(self.api.list_questionnaires)
        if items is None:
            return
        self.questionnaires_by_id = {item["id"]: item for item in items}
        self.questionnaire_ids = {item["titre"]: item["id"] for item in items}
        self.questionnaire_combo["values"] = list(self.questionnaire_ids)
        if items:
            self.questionnaire_var.set(items[0]["titre"])
            self.load_sessions()

    def load_sessions(self, _event=None) -> None:
        """
        Charge sessions et synchronise l'affichage avec le résultat obtenu.
        
        Paramètres :
            _event : donnée nécessaire au traitement de « event ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        questionnaire_id = self.questionnaire_ids.get(self.questionnaire_var.get())
        if questionnaire_id is None:
            return
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        items = run_api_action(lambda: self.api.list_sessions(questionnaire_id))
        if items is None:
            return
        self.sessions_by_id = {item["id"]: item for item in items}
        self.session_ids = {
            f"{item['nom_session']} — {item['statut']}": item["id"]
            for item in items
        }
        self.session_combo["values"] = list(self.session_ids)
        self.session_var.set(next(iter(self.session_ids), ""))
        self._clear_results()

    def _clear_results(self) -> None:
        """
        Effectue le traitement correspondant à clear results dans le contexte de cette fenêtre.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        self.last_stats = None
        self.participations = []
        for value in self.values.values():
            value.set("—")
        self.questionnaire_info_var.set("Questionnaire : —")
        self.session_info_var.set("Session : —")
        self.session_meta_var.set("Mode / statut : —")
        # Met à jour le contenu du tableau affiché dans l'interface.
        if hasattr(self, "tree"):
            self.tree.delete(*self.tree.get_children())

    def load_statistics(self) -> None:
        """
        Charge statistics et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self.session_ids.get(self.session_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if session_id is None:
            messagebox.showwarning("Aucune session", "Choisissez une session.")
            return

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        stats = run_api_action(lambda: self.api.get_statistics(session_id))
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        participations = run_api_action(lambda: self.api.list_participations(session_id))
        if stats is None or participations is None:
            return

        self.last_stats = stats
        self.participations = participations
        self.values["participants"].set(str(stats["nombre_participations"]))
        self.values["evalues"].set(str(stats["nombre_participations_evaluees"]))
        self.values["moyenne"].set(f"{stats['moyenne']:.2f} / 20")
        self.values["minimum"].set(self._format_score(stats.get("score_minimum")))
        self.values["maximum"].set(self._format_score(stats.get("score_maximum")))
        self.values["reussite"].set(f"{stats['taux_reussite']:.1f} %")

        questionnaire_title = self.questionnaire_var.get() or "—"
        session = self.sessions_by_id.get(session_id, {})
        self.questionnaire_info_var.set(f"Questionnaire : {questionnaire_title}")
        self.session_info_var.set(f"Session : {session.get('nom_session') or self.session_var.get() or '—'}")
        self.session_meta_var.set(
            "Mode : {mode}   |   Statut : {statut}   |   Début : {debut}   |   Fin : {fin}".format(
                mode=session.get("mode") or "—",
                statut=session.get("statut") or "—",
                debut=session.get("date_debut") or "—",
                fin=session.get("date_fin") or "—",
            )
        )
        self._fill_participation_table(session.get("mode") or "individuel")

    def _fill_participation_table(self, session_mode: str) -> None:
        """
        Effectue le traitement correspondant à fill participation table dans le contexte de cette fenêtre.
        
        Paramètres :
            session_mode : donnée nécessaire au traitement de « session mode ».
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        # Met à jour le contenu du tableau affiché dans l'interface.
        self.tree.delete(*self.tree.get_children())

        # Conserve tous les noms et les répartit sur plusieurs lignes. La hauteur
        # du tableau est ensuite adaptée à l'équipe qui nécessite le plus de place.
        prepared_rows = []
        maximum_line_count = 1
        for item in self.participations:
            participant_id = item["participant_id"]
            name = self._wrap_participant_text(
                self._participant_name(participant_id, session_mode)
            )
            maximum_line_count = max(maximum_line_count, name.count("\n") + 1)
            prepared_rows.append((item, name))

        ttk.Style(self).configure(
            "Statistics.Treeview",
            rowheight=max(54, maximum_line_count * 19),
        )

        for item, name in prepared_rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    name,
                    "—" if item.get("score") is None else f"{float(item['score']):.2f}",
                    self._wrap_text(item.get("commentaire_initial"), 38),
                    self._wrap_text(item.get("commentaire_final"), 46),
                ),
            )

    @staticmethod
    def _wrap_participant_text(value, width: int = 32) -> str:
        """
        Répartit le nom d'un élève ou la composition complète d'une équipe sur
        plusieurs lignes afin que le contenu reste visible dans le tableau.

        Paramètres :
            value : texte à afficher dans la colonne participant.
            width : nombre approximatif de caractères par ligne.

        Retour :
            Texte complet contenant les retours à la ligne nécessaires.
        """
        text = "" if value is None else str(value).strip()
        if not text:
            return "—"
        return "\n".join(
            wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
            or [text]
        )

    def _participant_name(self, participant_id: int, session_mode: str) -> str:
        """
        Effectue le traitement correspondant à participant name dans le contexte de cette fenêtre.
        
        Paramètres :
            participant_id : donnée nécessaire au traitement de « participant id ».
            session_mode : donnée nécessaire au traitement de « session mode ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        cache_key = (session_mode, participant_id)
        if cache_key in self.participant_names:
            return self.participant_names[cache_key]

        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        if session_mode == "equipe":
            participant = run_api_action(lambda: self.api.get_equipe(participant_id))
            if isinstance(participant, dict):
                team_name = participant.get("nom_equipe") or f"Équipe {participant_id}"
                members = [self._member_name(member) for member in participant.get("membres") or []]
                name = f"{team_name} : {', '.join(members)}" if members else team_name
                self.participant_names[cache_key] = name
                return name
        else:
            participant = run_api_action(lambda: self.api.get_eleve(participant_id))
            if isinstance(participant, dict):
                name = f"{participant.get('prenom') or ''} {participant.get('nom_eleve') or ''}".strip()
                if name:
                    self.participant_names[cache_key] = name
                    return name

        return f"Participant {participant_id}"

    @staticmethod
    def _member_name(member: dict) -> str:
        """
        Effectue le traitement correspondant à member name dans le contexte de cette fenêtre.
        
        Paramètres :
            member : donnée nécessaire au traitement de « member ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return (
            f"{member.get('prenom') or ''} {member.get('nom_eleve') or ''}".strip()
            or f"Élève {member.get('id', '?')}"
        )

    @staticmethod
    def _wrap_text(value, width: int) -> str:
        """
        Effectue le traitement correspondant à wrap text dans le contexte de cette fenêtre.
        
        Paramètres :
            value : donnée nécessaire au traitement de « value ».
            width : donnée nécessaire au traitement de « width ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        text = "" if value is None else str(value).strip()
        if not text:
            return "—"
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            lines.extend(
                wrap(paragraph, width=width, break_long_words=False, break_on_hyphens=False)
                or [""]
            )
        return "\n".join(lines[:4])

    def show_report(self) -> None:
        """
        Affiche report et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        session_id = self.session_ids.get(self.session_var.get())
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        if session_id is None:
            messagebox.showwarning("Aucune session", "Choisissez une session.")
            return
        if self.last_stats is None or not self.participations:
            self.load_statistics()
        # Exécute l'opération correspondante auprès du serveur puis récupère sa réponse.
        report = run_api_action(lambda: self.api.get_report(session_id))
        if report is None or self.last_stats is None:
            return

        window = tk.Toplevel(self)
        window.title("Rapport détaillé de session")
        window.geometry("1050x680")
        window.minsize(800, 500)

        text = tk.Text(window, wrap="word", padx=15, pady=15)
        scroll = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        text.insert("end", f"Questionnaire : {self.questionnaire_var.get()}\n")
        text.insert("end", f"Session : {self.sessions_by_id.get(session_id, {}).get('nom_session', '—')}\n")
        text.insert("end", f"Date de génération : {report['date_generation']}\n\n")
        text.insert("end", "INDICATEURS GLOBAUX\n")
        text.insert("end", f"Participations : {self.last_stats['nombre_participations']}\n")
        text.insert("end", f"Participations évaluées : {self.last_stats['nombre_participations_evaluees']}\n")
        text.insert("end", f"Moyenne : {self.last_stats['moyenne']:.2f} / 20\n")
        text.insert("end", f"Score minimum : {self._format_score(self.last_stats.get('score_minimum'))}\n")
        text.insert("end", f"Score maximum : {self._format_score(self.last_stats.get('score_maximum'))}\n")
        text.insert("end", f"Taux de réussite : {self.last_stats['taux_reussite']:.1f} %\n\n")
        text.insert("end", "DÉTAIL DES PARTICIPANTS\n")

        mode = self.sessions_by_id.get(session_id, {}).get("mode", "individuel")
        for index, item in enumerate(self.participations, start=1):
            name = self._participant_name(item["participant_id"], mode)
            text.insert("end", f"\n{index}. {name}\n")
            text.insert("end", f"Score : {self._format_score(item.get('score'))}\n")
            text.insert("end", f"Commentaire initial : {item.get('commentaire_initial') or '—'}\n")
            text.insert("end", f"Commentaire final : {item.get('commentaire_final') or '—'}\n")

        text.configure(state="disabled")

    def show_chart(self) -> None:
        """
        Affiche chart et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.last_stats is None:
            self.load_statistics()
        if self.last_stats is None:
            return

        values = [
            self.last_stats.get("moyenne") or 0,
            self.last_stats.get("score_minimum") or 0,
            self.last_stats.get("score_maximum") or 0,
        ]
        window = tk.Toplevel(self)
        window.title("Graphique des scores")
        window.geometry("700x450")
        figure = Figure(figsize=(7, 4), dpi=100)
        axis = figure.add_subplot(111)
        axis.bar(("Moyenne", "Minimum", "Maximum"), values)
        axis.set_ylim(0, 20)
        axis.set_ylabel("Score sur 20")
        axis.set_title("Résultats de la session")
        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def export_csv(self) -> None:
        """
        Exporte csv et synchronise l'affichage avec le résultat obtenu.
        
        Retour :
            Aucun. L'état de l'interface ou les données courantes sont directement mis à jour.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        if self.last_stats is None:
            self.load_statistics()
        if self.last_stats is None:
            return

        session_id = self.session_ids.get(self.session_var.get())
        session = self.sessions_by_id.get(session_id, {})
        path = filedialog.asksaveasfilename(
            title="Exporter les statistiques",
            defaultextension=".csv",
            filetypes=(("Fichier CSV", "*.csv"),),
        )
        if not path:
            return

        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(("Questionnaire", self.questionnaire_var.get()))
                writer.writerow(("Session", session.get("nom_session") or ""))
                writer.writerow(("Mode", session.get("mode") or ""))
                writer.writerow(("Statut", session.get("statut") or ""))
                writer.writerow(())
                writer.writerow(("Indicateur", "Valeur"))
                for key, label in (
                    ("nombre_participations", "Nombre de participations"),
                    ("nombre_participations_evaluees", "Participations évaluées"),
                    ("moyenne", "Moyenne"),
                    ("score_minimum", "Score minimum"),
                    ("score_maximum", "Score maximum"),
                    ("taux_reussite", "Taux de réussite"),
                ):
                    writer.writerow((label, self.last_stats.get(key)))
                writer.writerow(())
                writer.writerow(("Participant", "Score", "Commentaire initial", "Commentaire final"))
                mode = session.get("mode", "individuel")
                for item in self.participations:
                    writer.writerow((
                        self._participant_name(item["participant_id"], mode),
                        item.get("score"),
                        item.get("commentaire_initial") or "",
                        item.get("commentaire_final") or "",
                    ))
        except OSError as error:
            messagebox.showerror("Export impossible", str(error))
            return
        # Informe l'utilisateur du résultat de l'opération ou d'une erreur de saisie.
        messagebox.showinfo("Export terminé", "Le fichier CSV détaillé a été créé.")

    @staticmethod
    def _format_score(value) -> str:
        """
        Effectue le traitement correspondant à format score dans le contexte de cette fenêtre.
        
        Paramètres :
            value : donnée nécessaire au traitement de « value ».
        
        Retour :
            Données calculées ou récupérées par la méthode.
        
        Traitement :
            Les contrôles de saisie et les erreurs attendues sont pris en compte avant
            d'actualiser les widgets concernés ou de poursuivre la navigation.
        """
        return "—" if value is None else f"{float(value):.2f} / 20"
