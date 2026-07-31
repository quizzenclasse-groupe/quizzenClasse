# database/features/management_quest.py
# *******************************************************
# Nom ......... : management_quest.py
# Rôle ........ : Orchestre les cas d'usage liés aux
#                 questionnaires, questions, propositions,
#                 sessions, participants et rapports, vérifie
#                 les droits des utilisateurs et délègue la
#                 persistance aux services spécialisés.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile \
#                 database/features/management_quest.py
# Usage ....... : Importer puis instancier le contrôleur :
#                 ManagementQuestionnaire()
# *******************************************************
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from database.models.models_evaluation import (
    Proposition,
    Question,
    Questionnaire,
    RapportSession,
    SessionQuestionnaire,
)

if TYPE_CHECKING:
    from database.models.models_evaluation import (
        StatistiquesSession,
    )
    from database.models.models_participants import (
        Participant,
    )
    from database.models.models_utilisateurs import (
        Enseignant,
        Utilisateur,
    )
    from database.services.questionnaire_bd import (
        QuestionnaireBD,
    )
    from database.services.session_questionnaire_bd import (
        SessionQuestionnaireBD,
    )
    
class ManagementQuestionnaire:
    """
    Contrôleur d'orchestration pour la gestion des questionnaires,
    des questions, des propositions, des sessions et des rapports.

    Cette classe ne porte pas l'état métier du questionnaire :
    elle vérifie les droits, appelle les méthodes du modèle,
    puis délègue la persistance aux objets *BD / repositories.
    """

    @staticmethod
    def _est_admin(utilisateur: "Utilisateur") -> bool:
        return getattr(utilisateur, "type_utilisateur", None) == "admin"

    def _verifier_droits_sur_questionnaire(
        self,
        utilisateur: "Utilisateur",
        questionnaire: "Questionnaire",
    ) -> None:
        """
        Autorise l'action si l'utilisateur est admin ou auteur du questionnaire.
        """
        if self._est_admin(utilisateur):
            return

        auteur_id = getattr(questionnaire, "auteur_id", None)
        auteur = getattr(questionnaire, "auteur", None)

        if auteur_id == utilisateur.id:
            return
        if auteur is not None and getattr(auteur, "id", None) == utilisateur.id:
            return

        raise PermissionError(
            "Vous ne pouvez agir que sur vos propres questionnaires."
        )

    def _verifier_droits_sur_session(
        self,
        utilisateur: Utilisateur,
        session: SessionQuestionnaire,
    ) -> None:
        """
        Autorise l'action si l'utilisateur est administrateur ou auteur
        du questionnaire associé à la session.
        """
        if self._est_admin(utilisateur):
            return

        questionnaire = getattr(
            session,
            "questionnaire",
            None,
        )

        if questionnaire is None:
            raise ValueError(
                "La session n'est associée à aucun questionnaire."
            )

        auteur_id = getattr(
            questionnaire,
            "enseignant_id",
            None,
        )
        auteur = getattr(
            questionnaire,
            "auteur",
            None,
        )

        if auteur_id == utilisateur.id:
            return

        if (
            auteur is not None
            and getattr(auteur, "id", None) == utilisateur.id
        ):
            return

        raise PermissionError(
            "Vous ne pouvez agir que sur vos propres sessions."
        )

    def chargerQuestionnaire(
        self,
        questionnaire_id: int,
        questionnaire_bd: "QuestionnaireBD",
    ) -> "Questionnaire":
        """
        Charge un questionnaire par identifiant.
        """
        questionnaire = questionnaire_bd.charger(questionnaire_id)
        if questionnaire is None:
            raise ValueError(
                f"Aucun questionnaire ne correspond à l'identifiant {questionnaire_id}."
            )
        return questionnaire


    # ---------------------------
    # GESTION DES QUESTIONNAIRES
    # ---------------------------

    def creerQuestionnaire(
        self,
        enseignant: Enseignant,
        questionnaire_bd: QuestionnaireBD,
    ) -> Questionnaire:
        """
        Crée un questionnaire, ses questions et leurs propositions, puis
        délègue leur sauvegarde à QuestionnaireBD.
        """
        self._verifier_identifiant_utilisateur(enseignant)

        print("Bienvenue dans la création de questionnaire.")

        titre = input("Quel est le titre du questionnaire ? ").strip()
        niveau = input("À quel niveau s'adresse-t-il ? ").strip()
        matiere = input("Quelle matière concerne-t-il ? ").strip()
        difficulte = input(
            "Quel est son niveau de difficulté ? "
        ).strip()

        if not all([titre, niveau, matiere, difficulte]):
            raise ValueError(
                "Le titre, le niveau, la matière et la difficulté "
                "sont obligatoires."
            )

        questionnaire = Questionnaire(
            titre=titre,
            niveau=niveau,
            matiere=matiere,
            difficulte=difficulte,
            date_creation=date.today(),
            auteur=enseignant,
        )

        questions: list[Question] = []

        try:
            nombre_questions = int(
                input(
                    "Combien de questions aura votre questionnaire ? "
                )
            )
        except ValueError as exc:
            raise ValueError(
                "Le nombre de questions doit être un entier."
            ) from exc

        if nombre_questions <= 0:
            raise ValueError(
                "Un questionnaire doit contenir au moins une question."
            )

        for indice_question in range(nombre_questions):
            enonce = input(
                "Veuillez saisir la question numéro "
                f"{indice_question + 1} : "
            ).strip()

            if not enonce:
                raise ValueError(
                    "L'énoncé de la question ne peut pas être vide."
                )

            type_question = input(
                "Question ouverte (O) ou fermée (F) ? "
            ).strip().upper()

            if type_question not in {"O", "F"}:
                raise ValueError(
                    "Le type de question doit être 'O' ou 'F'."
                )

            question = Question(
                enonce=enonce,
                type_question=type_question,
                questionnaire=questionnaire,
            )

            propositions: list[Proposition] = []

            if type_question == "O":
                print(
                    "Question ouverte : création des réponses "
                    "attendues."
                )

                try:
                    nombre_propositions = int(
                        input(
                            "Combien de réponses attendues voulez-vous "
                            "associer à cette question ? "
                        )
                    )
                except ValueError as exc:
                    raise ValueError(
                        "Le nombre de réponses attendues doit être "
                        "un entier."
                    ) from exc

                if nombre_propositions <= 0:
                    raise ValueError(
                        "Une question ouverte doit contenir au moins "
                        "une réponse attendue."
                    )

                for indice_proposition in range(nombre_propositions):
                    libelle = input(
                        "Veuillez saisir la réponse attendue numéro "
                        f"{indice_proposition + 1} : "
                    ).strip()

                    if not libelle:
                        raise ValueError(
                            "Une réponse attendue ne peut pas être vide."
                        )

                    propositions.append(
                        Proposition(
                            libelle=libelle,
                            est_correcte=True,
                            question=question,
                        )
                    )

            else:
                print(
                    "Question fermée : création des propositions "
                    "VRAI / FAUX."
                )

                reponse_correcte = input(
                    "Quelle est la bonne réponse ? "
                    "Tapez V pour VRAI ou F pour FAUX : "
                ).strip().upper()

                if reponse_correcte not in {"V", "F"}:
                    raise ValueError(
                        "La bonne réponse doit être 'V' ou 'F'."
                    )

                propositions.extend(
                    [
                        Proposition(
                            libelle="VRAI",
                            est_correcte=(reponse_correcte == "V"),
                            question=question,
                        ),
                        Proposition(
                            libelle="FAUX",
                            est_correcte=(reponse_correcte == "F"),
                            question=question,
                        ),
                    ]
                )

            question.propositions = propositions
            questions.append(question)

        questionnaire.questions = questions
        questionnaire_bd.sauvegarder(questionnaire)

        return questionnaire


    def afficherQuestionnaires(
        self,
        enseignant: Enseignant,
        questionnaire_bd: QuestionnaireBD,
    ) -> list[Questionnaire]:
        """
        Affiche et retourne les questionnaires appartenant à un enseignant.
        """
        enseignant_id = self._verifier_identifiant_utilisateur(enseignant)
        questionnaires = questionnaire_bd.chargerParEnseignant(
            enseignant_id
        )

        if not questionnaires:
            print("Aucun questionnaire n'est associé à cet enseignant.")
            return []

        for index, questionnaire in enumerate(questionnaires, start=1):
            auteur = getattr(questionnaire, "auteur", None)
            nom_auteur = getattr(
                auteur,
                "nom_utilisateur",
                "auteur non renseigné",
            )

            print(
                f"{index}. identifiant : {questionnaire.id} | "
                f"titre : {questionnaire.titre} | "
                f"niveau : {questionnaire.niveau} | "
                f"matière : {questionnaire.matiere} | "
                f"difficulté : {questionnaire.difficulte} | "
                f"créé le : {questionnaire.date_creation} | "
                f"auteur : {nom_auteur}"
            )

        return questionnaires


    def modifierQuestionnaire(
        self,
        utilisateur: Utilisateur,
        questionnaire_bd: QuestionnaireBD,
        questionnaire_id: int,
    ) -> Questionnaire:
        """
        Modifie l'énoncé d'une question ou le libellé d'une proposition.
        """
        questionnaire = self.chargerQuestionnaire(
            questionnaire_id,
            questionnaire_bd,
        )
        self._verifier_droits_sur_questionnaire(
            utilisateur,
            questionnaire,
        )

        if not questionnaire.questions:
            raise ValueError(
                "Ce questionnaire ne contient aucune question."
            )

        choix = input(
            "Modifier une question (Q) ou une proposition (P) ? "
        ).strip().upper()

        if choix not in {"Q", "P"}:
            raise ValueError("Le choix doit être 'Q' ou 'P'.")

        for index, question in enumerate(
            questionnaire.questions,
            start=1,
        ):
            print(f"{index}. {question.enonce}")

        try:
            numero_question = int(
                input("Numéro de la question : ")
            )
        except ValueError as exc:
            raise ValueError(
                "Le numéro de la question doit être un entier."
            ) from exc

        if not 1 <= numero_question <= len(questionnaire.questions):
            raise ValueError(
                "Le numéro de la question est invalide."
            )

        question = questionnaire.questions[numero_question - 1]

        if choix == "Q":
            nouvel_enonce = input("Nouvel énoncé : ").strip()

            if not nouvel_enonce:
                raise ValueError(
                    "L'énoncé de la question ne peut pas être vide."
                )

            question.enonce = nouvel_enonce

        else:
            if not question.propositions:
                raise ValueError(
                    "Cette question ne contient aucune proposition."
                )

            for index, proposition in enumerate(
                question.propositions,
                start=1,
            ):
                print(f"{index}. {proposition.libelle}")

            try:
                numero_proposition = int(
                    input("Numéro de la proposition : ")
                )
            except ValueError as exc:
                raise ValueError(
                    "Le numéro de la proposition doit être un entier."
                ) from exc

            if not 1 <= numero_proposition <= len(
                question.propositions
            ):
                raise ValueError(
                    "Le numéro de la proposition est invalide."
                )

            nouveau_libelle = input(
                "Nouveau libellé : "
            ).strip()

            if not nouveau_libelle:
                raise ValueError(
                    "Le libellé ne peut pas être vide."
                )

            proposition = question.propositions[
                numero_proposition - 1
            ]
            proposition.libelle = nouveau_libelle

        questionnaire_bd.sauvegarder(questionnaire)
        return questionnaire

    def dupliquerQuestionnaire(
        self,
        enseignant: Enseignant,
        questionnaire_bd: QuestionnaireBD,
        questionnaire: Questionnaire,
    ) -> Questionnaire:
        """Duplique un questionnaire et affecte la copie à l'enseignant."""
        self._verifier_droits_sur_questionnaire(
            enseignant,
            questionnaire,
        )

        copie = questionnaire.dupliquer(auteur=enseignant)
        questionnaire_bd.sauvegarder(copie)

        return copie

    def ajouterQuestion(
        self,
        utilisateur: Utilisateur,
        questionnaire_bd: QuestionnaireBD,
        questionnaire_id: int,
    ) -> Question:
        """Ajoute une question à un questionnaire existant."""
        questionnaire = self.chargerQuestionnaire(
            questionnaire_id,
            questionnaire_bd,
        )
        self._verifier_droits_sur_questionnaire(
            utilisateur,
            questionnaire,
        )

        enonce = input(
            "Veuillez saisir l'énoncé de la question : "
        ).strip()

        if not enonce:
            raise ValueError(
                "L'énoncé de la question ne peut pas être vide."
            )

        type_question = input(
            "Question ouverte (O) ou fermée (F) ? "
        ).strip().upper()

        if type_question not in {"O", "F"}:
            raise ValueError(
                "Le type de question doit être 'O' ou 'F'."
            )

        question = Question(
            enonce=enonce,
            type_question=type_question,
            questionnaire=questionnaire,
        )

        if questionnaire.questions is None:
            questionnaire.questions = []

        if question not in questionnaire.questions:
            questionnaire.questions.append(question)

        questionnaire_bd.sauvegarder(questionnaire)
        return question

    def retirerQuestion(
        self,
        utilisateur: Utilisateur,
        questionnaire_bd: QuestionnaireBD,
        questionnaire: Questionnaire,
        question: Question,
    ) -> None:
        """Retire une question d'un questionnaire."""
        self._verifier_droits_sur_questionnaire(
            utilisateur,
            questionnaire,
        )

        questionnaire.retirerQuestion(question)
        questionnaire_bd.sauvegarder(questionnaire)

    def ajouterProposition(
        self,
        utilisateur: Utilisateur,
        questionnaire_bd: QuestionnaireBD,
        questionnaire_id: int,
    ) -> Proposition:
        """Ajoute une proposition à une question sélectionnée."""
        questionnaire = self.chargerQuestionnaire(
            questionnaire_id,
            questionnaire_bd,
        )
        self._verifier_droits_sur_questionnaire(
            utilisateur,
            questionnaire,
        )

        if not questionnaire.questions:
            raise ValueError(
                "Ce questionnaire ne contient aucune question."
            )

        for index, question in enumerate(
            questionnaire.questions,
            start=1,
        ):
            print(f"{index}. {question.enonce}")

        try:
            numero_question = int(
                input("Numéro de la question : ")
            )
        except ValueError as exc:
            raise ValueError(
                "Le numéro de la question doit être un entier."
            ) from exc

        if not 1 <= numero_question <= len(questionnaire.questions):
            raise ValueError(
                "Le numéro de la question est invalide."
            )

        question = questionnaire.questions[numero_question - 1]
        libelle = input(
            "Veuillez saisir le libellé de la proposition : "
        ).strip()

        if not libelle:
            raise ValueError(
                "Le libellé de la proposition ne peut pas être vide."
            )

        reponse = input(
            "Cette proposition est-elle correcte ? O/N : "
        ).strip().upper()

        if reponse not in {"O", "N"}:
            raise ValueError("La réponse doit être 'O' ou 'N'.")

        proposition = Proposition(
            libelle=libelle,
            est_correcte=(reponse == "O"),
            question=question,
        )

        if question.propositions is None:
            question.propositions = []

        if proposition not in question.propositions:
            question.propositions.append(proposition)

        questionnaire_bd.sauvegarder(questionnaire)
        return proposition

    def retirerProposition(
        self,
        utilisateur: Utilisateur,
        questionnaire_bd: QuestionnaireBD,
        question: Question,
        proposition: Proposition,
    ) -> None:
        """Retire une proposition d'une question."""
        questionnaire = question.questionnaire
        self._verifier_droits_sur_questionnaire(
            utilisateur,
            questionnaire,
        )

        question.retirerProposition(proposition)
        questionnaire_bd.sauvegarder(questionnaire)

    # --------------------
    # GESTION DES SESSIONS
    # ---------------------

    def creerSession(
        self,
        enseignant: Enseignant,
        session_questionnaire_bd: SessionQuestionnaireBD,
        questionnaire: Questionnaire,
        nom_session: str,
        mode: str,
    ) -> SessionQuestionnaire:
        """Crée une session rattachée à un questionnaire."""
        self._verifier_droits_sur_questionnaire(
            enseignant,
            questionnaire,
        )

        nom_session = nom_session.strip()
        mode = mode.strip()

        if not nom_session:
            raise ValueError(
                "Le nom de la session est obligatoire."
            )

        if not mode:
            raise ValueError(
                "Le mode de la session est obligatoire."
            )

        session = SessionQuestionnaire.creer(
            questionnaire=questionnaire,
            titre=nom_session,
            mode=mode,
        )

        session_questionnaire_bd.sauvegarder(session)
        return session

    def demarrerSession(
        self,
        enseignant: Enseignant,
        session_questionnaire_bd: SessionQuestionnaireBD,
    ) -> SessionQuestionnaire | None:
        """
        Demande de sélectionner une session créée, la démarre, puis la
        sauvegarde.
        """
        enseignant_id = self._verifier_identifiant_utilisateur(
            enseignant
        )
        sessions = session_questionnaire_bd.chargerParEnseignant(
            enseignant_id
        )
        sessions_creees = [
            session
            for session in sessions
            if session.date_debut is None
            and session.date_fin is None
        ]

        if not sessions_creees:
            print("Aucune session créée n'est disponible.")
            return None

        for index, session in enumerate(sessions_creees, start=1):
            print(f"{index}. {session.nom_session}")

        try:
            numero = int(
                input("Numéro de la session à démarrer : ")
            )
        except ValueError as exc:
            raise ValueError(
                "Le numéro de la session doit être un entier."
            ) from exc

        if not 1 <= numero <= len(sessions_creees):
            raise ValueError(
                "Le numéro de la session est invalide."
            )

        session = sessions_creees[numero - 1]
        self._verifier_droits_sur_session(enseignant, session)
        session.lancer()

        session_questionnaire_bd.sauvegarder(session)
        return session

    def cloturerSession(
        self,
        enseignant: Enseignant,
        session_questionnaire_bd: SessionQuestionnaireBD,
    ) -> SessionQuestionnaire | None:
        """
        Demande de sélectionner une session démarrée, la clôture, puis la
        sauvegarde.
        """
        enseignant_id = self._verifier_identifiant_utilisateur(
            enseignant
        )
        sessions = session_questionnaire_bd.chargerParEnseignant(
            enseignant_id
        )
        sessions_demarrees = [
            session
            for session in sessions
            if session.date_debut is not None
            and session.date_fin is None
        ]

        if not sessions_demarrees:
            print("Aucune session démarrée n'est disponible.")
            return None

        for index, session in enumerate(
            sessions_demarrees,
            start=1,
        ):
            print(f"{index}. {session.nom_session}")

        try:
            numero = int(
                input("Numéro de la session à clôturer : ")
            )
        except ValueError as exc:
            raise ValueError(
                "Le numéro de la session doit être un entier."
            ) from exc

        if not 1 <= numero <= len(sessions_demarrees):
            raise ValueError(
                "Le numéro de la session est invalide."
            )

        session = sessions_demarrees[numero - 1]
        self._verifier_droits_sur_session(enseignant, session)
        session.clore()

        session_questionnaire_bd.sauvegarder(session)
        return session


    @staticmethod
    def _statut_session(
        session: SessionQuestionnaire,
    ) -> str:
        if session.date_fin is not None:
            return "clôturée"

        if session.date_debut is not None:
            return "démarrée"

        return "créée"

    

    def listeParticipants(
        self,
        enseignant: Enseignant,
        session_questionnaire_bd: SessionQuestionnaireBD,
    ) -> list[Participant]:
        """Affiche et retourne les participants d'une session sélectionnée."""
        enseignant_id = self._verifier_identifiant_utilisateur(
            enseignant
        )
        sessions = session_questionnaire_bd.chargerParEnseignant(
            enseignant_id
        )

        if not sessions:
            print("Aucune session n'est associée à cet enseignant.")
            return []

        for index, session in enumerate(sessions, start=1):
            print(f"{index}. {session.nom_session}")

        try:
            numero = int(input("Numéro de la session : "))
        except ValueError as exc:
            raise ValueError(
                "Le numéro de la session doit être un entier."
            ) from exc

        if not 1 <= numero <= len(sessions):
            raise ValueError(
                "Le numéro de la session est invalide."
            )

        session = sessions[numero - 1]
        self._verifier_droits_sur_session(enseignant, session)
        participants = (
            session_questionnaire_bd.chargerParticipantsParSession(
                session.id
            )
        )

        if not participants:
            print(
                "Aucun participant n'est associé à cette session."
            )
            return []

        for index, participant in enumerate(
            participants,
            start=1,
        ):
            print(f"{index}. {participant}")

        return participants

    def listeSessions(
        self,
        enseignant: Enseignant,
        session_questionnaire_bd: SessionQuestionnaireBD,
    ) -> list[SessionQuestionnaire]:
        """Affiche et retourne les sessions appartenant à l'enseignant."""
        enseignant_id = self._verifier_identifiant_utilisateur(
            enseignant
        )
        sessions = session_questionnaire_bd.chargerParEnseignant(
            enseignant_id
        )

        if not sessions:
            print("Aucune session n'est associée à cet enseignant.")
            return []

        for index, session in enumerate(sessions, start=1):

            statut = self.statut_session(session)

            print(
                f"{index}. {session.nom_session} "
                f"- mode : {session.mode} "
                f"- statut : {statut}"
            )

        return sessions

    def genererRapport(
        self,
        utilisateur: Utilisateur,
        session_questionnaire_bd: SessionQuestionnaireBD,
        session: SessionQuestionnaire,
        statistiques: StatistiquesSession | None = None,
    ) -> RapportSession:
        """Génère et sauvegarde le rapport d'une session."""
        self._verifier_droits_sur_session(utilisateur, session)

        rapport = RapportSession.generer_depuis_session(
            session,
            statistiques=statistiques,
        )

        session_questionnaire_bd.sauvegarderRapport(rapport)
        return rapport

    