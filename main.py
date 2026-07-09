# main.py
from __future__ import annotations

import argparse
import os
from getpass import getpass
from pathlib import Path
from typing import Callable, Sequence, TypeVar

import database.models  # Enregistre tous les modèles dans le mapping SQLAlchemy.
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as OrmSession

from database.base import Model
from database.engine import Session, engine
from database.models.models_evaluation import (
    Proposition,
    Question,
    Questionnaire,
    RapportSession,
    SessionQuestionnaire,
    StatistiquesSession,
)
from database.models.models_participants import (
    Eleve,
    Equipe,
    Participant,
    Participation,
)
from database.models.models_scolaire import Etablissement
from database.models.models_utilisateurs import Enseignant
from database.services.connexion_service import ConnexionService
from database.services.etablissements_loader import (
    load_etablissements_from_csv,
)


T = TypeVar("T")

CHEMIN_CSV_PAR_DEFAUT = Path(
    os.getenv(
        "EDU_CSV_PATH",
        "data/raw/education/fr-en-annuaire-education.csv",
    )
)


# ============================================================================
# OUTILS D'AFFICHAGE ET DE SAISIE
# ============================================================================


def afficher_titre(titre: str) -> None:
    largeur = 64
    print()
    print("=" * largeur)
    print(titre.center(largeur))
    print("=" * largeur)


def afficher_message_erreur(message: str) -> None:
    print(f"\nErreur : {message}")


def demander_texte(
    libelle: str,
    *,
    obligatoire: bool = True,
) -> str:
    while True:
        valeur = input(libelle).strip()

        if valeur or not obligatoire:
            return valeur

        print("Cette valeur est obligatoire.")


def demander_entier(
    libelle: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    while True:
        valeur = input(libelle).strip()

        try:
            nombre = int(valeur)
        except ValueError:
            print("La valeur saisie doit être un entier.")
            continue

        if minimum is not None and nombre < minimum:
            print(f"La valeur minimale est {minimum}.")
            continue

        if maximum is not None and nombre > maximum:
            print(f"La valeur maximale est {maximum}.")
            continue

        return nombre


def demander_reel(
    libelle: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    while True:
        valeur = input(libelle).strip().replace(",", ".")

        try:
            nombre = float(valeur)
        except ValueError:
            print("La valeur saisie doit être un nombre.")
            continue

        if minimum is not None and nombre < minimum:
            print(f"La valeur minimale est {minimum}.")
            continue

        if maximum is not None and nombre > maximum:
            print(f"La valeur maximale est {maximum}.")
            continue

        return nombre


def demander_confirmation(libelle: str) -> bool:
    while True:
        valeur = input(f"{libelle} [O/N] : ").strip().upper()

        if valeur == "O":
            return True

        if valeur == "N":
            return False

        print("Saisissez O pour oui ou N pour non.")


def selectionner_element(
    elements: Sequence[T],
    afficher: Callable[[T], str],
    libelle: str,
) -> T | None:
    if not elements:
        print("Aucun élément disponible.")
        return None

    for index, element in enumerate(elements, start=1):
        print(f"{index}. {afficher(element)}")

    print("0. Annuler")

    choix = demander_entier(
        libelle,
        minimum=0,
        maximum=len(elements),
    )

    if choix == 0:
        return None

    return elements[choix - 1]


def valider_transaction(
    session: OrmSession,
    message_succes: str,
) -> bool:
    try:
        session.commit()
    except SQLAlchemyError as erreur:
        session.rollback()
        afficher_message_erreur(str(erreur))
        return False

    print(message_succes)
    return True


# ============================================================================
# INITIALISATION ET IMPORT DES ÉTABLISSEMENTS
# ============================================================================


def initialiser_base() -> None:
    """
    Crée les tables qui n'existent pas encore.

    Cette opération ne remplace pas une migration de schéma pour les tables
    déjà existantes.
    """
    Model.metadata.create_all(bind=engine)


def importer_etablissements(
    session: OrmSession,
    chemin_csv: Path = CHEMIN_CSV_PAR_DEFAUT,
    *,
    dedupe: bool = True,
    update_on_duplicate: bool = False,
) -> None:
    afficher_titre("IMPORT DES ÉTABLISSEMENTS")

    if not chemin_csv.exists():
        afficher_message_erreur(
            f"Le fichier CSV est introuvable : {chemin_csv}"
        )
        return

    try:
        nombre = load_etablissements_from_csv(
            session,
            chemin_csv,
            dedupe=dedupe,
            update_on_duplicate=update_on_duplicate,
        )
        session.commit()
    except (OSError, SQLAlchemyError, ValueError) as erreur:
        session.rollback()
        afficher_message_erreur(str(erreur))
        return

    print(
        f"OK : {nombre} établissement(s) importé(s) "
        f"depuis {chemin_csv}"
    )


def afficher_etablissements(session: OrmSession) -> None:
    afficher_titre("ÉTABLISSEMENTS")

    etablissements = list(
        session.scalars(
            select(Etablissement)
            .order_by(Etablissement.nom_etablissement)
            .limit(50)
        )
    )

    if not etablissements:
        print("Aucun établissement n'est enregistré.")
        return

    for etablissement in etablissements:
        print(
            f"{etablissement.id:>5} | "
            f"{etablissement.nom_etablissement} | "
            f"{etablissement.nom_departement}"
        )

    print(
        "\nAffichage limité aux 50 premiers établissements "
        "classés par nom."
    )


# ============================================================================
# AUTHENTIFICATION
# ============================================================================


def inscrire_enseignant(
    connexion_service: ConnexionService,
) -> None:
    afficher_titre("INSCRIPTION D'UN ENSEIGNANT")

    nom_utilisateur = demander_texte(
        "Nom d'utilisateur : "
    )
    mot_de_passe = getpass("Mot de passe : ")
    confirmation = getpass("Confirmation du mot de passe : ")

    if not mot_de_passe:
        afficher_message_erreur(
            "Le mot de passe ne peut pas être vide."
        )
        return

    if mot_de_passe != confirmation:
        afficher_message_erreur(
            "Les deux mots de passe ne correspondent pas."
        )
        return

    try:
        enseignant = connexion_service.inscrireEnseignant(
            nom_utilisateur,
            mot_de_passe,
        )
    except (ValueError, SQLAlchemyError) as erreur:
        afficher_message_erreur(str(erreur))
        return

    print(
        "Compte créé avec succès pour "
        f"{enseignant.nom_utilisateur}."
    )


def connecter_enseignant(
    connexion_service: ConnexionService,
) -> Enseignant | None:
    afficher_titre("CONNEXION")

    nom_utilisateur = demander_texte(
        "Nom d'utilisateur : "
    )
    mot_de_passe = getpass("Mot de passe : ")

    utilisateur = connexion_service.connecter(
        nom_utilisateur,
        mot_de_passe,
    )

    if utilisateur is None:
        afficher_message_erreur(
            "Nom d'utilisateur ou mot de passe incorrect."
        )
        return None

    if not isinstance(utilisateur, Enseignant):
        connexion_service.deconnecter()
        afficher_message_erreur(
            "Ce menu est réservé aux enseignants."
        )
        return None

    print(
        f"Connexion réussie : {utilisateur.nom_utilisateur}."
    )
    return utilisateur


# ============================================================================
# PARTICIPANTS ET ÉQUIPES
# ============================================================================


def creer_eleve(session: OrmSession) -> None:
    afficher_titre("CRÉATION D'UN ÉLÈVE")

    nom = demander_texte("Nom : ")
    prenom = demander_texte(
        "Prénom : ",
        obligatoire=False,
    )
    ville = demander_texte(
        "Ville : ",
        obligatoire=False,
    )
    code_postal = demander_texte(
        "Code postal : ",
        obligatoire=False,
    )

    eleve = Eleve(
        nom_eleve=nom,
        prenom=prenom or None,
        ville=ville or None,
        cp=code_postal or None,
    )

    session.add(eleve)

    if valider_transaction(
        session,
        "Élève créé avec succès.",
    ):
        print(f"Identifiant de l'élève : {eleve.id}")


def charger_eleves(session: OrmSession) -> list[Eleve]:
    return list(
        session.scalars(
            select(Eleve).order_by(
                Eleve.nom_eleve,
                Eleve.prenom,
            )
        )
    )


def afficher_eleves(session: OrmSession) -> None:
    afficher_titre("ÉLÈVES")

    eleves = charger_eleves(session)

    if not eleves:
        print("Aucun élève n'est enregistré.")
        return

    for eleve in eleves:
        prenom = eleve.prenom or ""
        print(
            f"{eleve.id:>5} | "
            f"{eleve.nom_eleve} {prenom}".rstrip()
        )


def former_equipe(session: OrmSession) -> None:
    afficher_titre("FORMATION D'UNE ÉQUIPE")

    eleves = charger_eleves(session)

    if len(eleves) < 3:
        print(
            "Au moins trois élèves doivent être enregistrés "
            "avant de former une équipe."
        )
        return

    for eleve in eleves:
        prenom = eleve.prenom or ""
        print(
            f"{eleve.id:>5} | "
            f"{eleve.nom_eleve} {prenom}".rstrip()
        )

    nom_equipe = demander_texte("Nom de l'équipe : ")

    saisie = demander_texte(
        "Identifiants des élèves séparés par des virgules : "
    )

    try:
        identifiants = {
            int(element.strip())
            for element in saisie.split(",")
            if element.strip()
        }
    except ValueError:
        afficher_message_erreur(
            "Les identifiants doivent être des entiers."
        )
        return

    if len(identifiants) != 3:
        afficher_message_erreur(
            "Une équipe doit contenir exactement trois élèves."
        )
        return

    membres = [
        eleve
        for eleve in eleves
        if eleve.id in identifiants
    ]

    if len(membres) != len(identifiants):
        afficher_message_erreur(
            "Au moins un identifiant d'élève est inconnu."
        )
        return

    try:
        equipe = Equipe.creer_depuis_eleves(
            nom_equipe,
            membres,
        )
    except ValueError as erreur:
        afficher_message_erreur(str(erreur))
        return

    session.add(equipe)

    if valider_transaction(
        session,
        "Équipe créée avec succès.",
    ):
        print(f"Identifiant de l'équipe : {equipe.id}")


def charger_participants(
    session: OrmSession,
) -> list[Participant]:
    return list(
        session.scalars(
            select(Participant).order_by(Participant.id)
        )
    )


def afficher_participants(session: OrmSession) -> None:
    afficher_titre("PARTICIPANTS")

    participants = charger_participants(session)

    if not participants:
        print("Aucun participant n'est enregistré.")
        return

    for participant in participants:
        if isinstance(participant, Eleve):
            libelle = (
                f"Élève : {participant.nom_eleve} "
                f"{participant.prenom or ''}"
            ).rstrip()
        elif isinstance(participant, Equipe):
            libelle = f"Équipe : {participant.nom_equipe}"
        else:
            libelle = participant.__class__.__name__

        print(f"{participant.id:>5} | {libelle}")


# ============================================================================
# QUESTIONNAIRES
# ============================================================================


def charger_questionnaires(
    session: OrmSession,
    enseignant: Enseignant,
) -> list[Questionnaire]:
    return list(
        session.scalars(
            select(Questionnaire)
            .where(
                Questionnaire.auteur_id
                == enseignant.id
            )
            .order_by(Questionnaire.id)
        )
    )


def creer_questionnaire(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("CRÉATION D'UN QUESTIONNAIRE QCM")

    titre = demander_texte("Titre : ")
    niveau = demander_texte(
        "Niveau : ",
        obligatoire=False,
    )
    matiere = demander_texte(
        "Matière : ",
        obligatoire=False,
    )
    difficulte = demander_texte(
        "Difficulté : ",
        obligatoire=False,
    )

    questionnaire = Questionnaire(
        titre=titre,
        niveau=niveau or None,
        matiere=matiere or None,
        difficulte=difficulte or None,
        auteur=enseignant,
    )

    nombre_questions = demander_entier(
        "Nombre de questions : ",
        minimum=1,
    )

    for numero_question in range(
        1,
        nombre_questions + 1,
    ):
        print()
        print(f"Question {numero_question}")

        enonce = demander_texte("Énoncé : ")

        question = Question(
            enonce=enonce,
            type_question="QCM",
        )

        questionnaire.ajouterQuestion(question)

        propositions: list[Proposition] = []

        for numero_proposition in range(1, 5):
            libelle = demander_texte(
                f"Proposition {numero_proposition} : "
            )

            propositions.append(
                Proposition(
                    libelle=libelle,
                    est_correcte=False,
                )
            )

        numero_correct = demander_entier(
            "Numéro de la bonne proposition : ",
            minimum=1,
            maximum=4,
        )

        for index, proposition in enumerate(
            propositions,
            start=1,
        ):
            proposition.est_correcte = (
                index == numero_correct
            )
            question.ajouterProposition(proposition)

    session.add(questionnaire)

    if valider_transaction(
        session,
        "Questionnaire créé avec succès.",
    ):
        print(
            f"Questionnaire n°{questionnaire.id} : "
            f"{questionnaire.titre}"
        )


def afficher_questionnaires(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("QUESTIONNAIRES")

    questionnaires = charger_questionnaires(
        session,
        enseignant,
    )

    if not questionnaires:
        print("Aucun questionnaire n'est enregistré.")
        return

    for questionnaire in questionnaires:
        print(
            f"{questionnaire.id:>5} | "
            f"{questionnaire.titre} | "
            f"{len(questionnaire.questions)} question(s)"
        )


# ============================================================================
# SESSIONS DE QUESTIONNAIRE
# ============================================================================


def charger_sessions_questionnaire(
    session: OrmSession,
    enseignant: Enseignant,
) -> list[SessionQuestionnaire]:
    return list(
        session.scalars(
            select(SessionQuestionnaire)
            .join(SessionQuestionnaire.questionnaire)
            .where(
                Questionnaire.auteur_id
                == enseignant.id
            )
            .order_by(SessionQuestionnaire.id)
        )
    )


def creer_session_questionnaire(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("CRÉATION D'UNE SESSION")

    questionnaires = charger_questionnaires(
        session,
        enseignant,
    )

    questionnaire = selectionner_element(
        questionnaires,
        lambda element: (
            f"{element.titre} "
            f"({len(element.questions)} question(s))"
        ),
        "Questionnaire choisi : ",
    )

    if questionnaire is None:
        return

    titre = demander_texte(
        "Titre de la session : "
    )
    mode = demander_texte(
        "Mode de la session : "
    )

    try:
        session_questionnaire = (
            SessionQuestionnaire.creer(
                questionnaire=questionnaire,
                titre=titre,
                mode=mode,
            )
        )
    except ValueError as erreur:
        afficher_message_erreur(str(erreur))
        return

    session.add(session_questionnaire)

    if valider_transaction(
        session,
        "Session créée avec succès.",
    ):
        print(
            f"Session n°{session_questionnaire.id} : "
            f"{session_questionnaire.nom_session}"
        )


def afficher_sessions(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("SESSIONS")

    sessions = charger_sessions_questionnaire(
        session,
        enseignant,
    )

    if not sessions:
        print("Aucune session n'est enregistrée.")
        return

    for session_questionnaire in sessions:
        if session_questionnaire.date_fin is not None:
            statut = "clôturée"
        elif session_questionnaire.date_debut is not None:
            statut = "en cours"
        else:
            statut = "créée"

        print(
            f"{session_questionnaire.id:>5} | "
            f"{session_questionnaire.nom_session} | "
            f"{statut}"
        )


def demarrer_session(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("DÉMARRAGE D'UNE SESSION")

    sessions = [
        element
        for element in charger_sessions_questionnaire(
            session,
            enseignant,
        )
        if element.date_debut is None
        and element.date_fin is None
    ]

    session_questionnaire = selectionner_element(
        sessions,
        lambda element: element.nom_session,
        "Session choisie : ",
    )

    if session_questionnaire is None:
        return

    try:
        session_questionnaire.lancer()
    except ValueError as erreur:
        afficher_message_erreur(str(erreur))
        return

    valider_transaction(
        session,
        "La session a été démarrée.",
    )


# ============================================================================
# PARTICIPATIONS, ÉVALUATION ET RAPPORT
# ============================================================================


def evaluer_participant(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("ÉVALUATION D'UN PARTICIPANT")

    sessions = [
        element
        for element in charger_sessions_questionnaire(
            session,
            enseignant,
        )
        if element.date_debut is not None
        and element.date_fin is None
    ]

    session_questionnaire = selectionner_element(
        sessions,
        lambda element: element.nom_session,
        "Session choisie : ",
    )

    if session_questionnaire is None:
        return

    participants = charger_participants(session)

    participant = selectionner_element(
        participants,
        lambda element: (
            getattr(
                element,
                "nom_equipe",
                None,
            )
            or (
                f"{getattr(element, 'nom_eleve', '')} "
                f"{getattr(element, 'prenom', '')}"
            ).strip()
            or element.__class__.__name__
        ),
        "Participant choisi : ",
    )

    if participant is None:
        return

    participation = session.scalar(
        select(Participation).where(
            Participation.session_questionnaire_id
            == session_questionnaire.id,
            Participation.participant_id
            == participant.id,
        )
    )

    if participation is None:
        participation = Participation(
            session_questionnaire_id=(
                session_questionnaire.id
            ),
            participant_id=participant.id,
        )
        session.add(participation)

    score = demander_reel(
        "Score sur 10 : ",
        minimum=0.0,
        maximum=10.0,
    )

    commentaire_initial = demander_texte(
        "Commentaire initial : ",
        obligatoire=False,
    )

    commentaire_final = demander_texte(
        "Commentaire final : ",
        obligatoire=False,
    )

    try:
        participation.evaluer(
            score=score,
            commentaire_initial=commentaire_initial,
            commentaire_final=commentaire_final,
        )
    except ValueError as erreur:
        session.rollback()
        afficher_message_erreur(str(erreur))
        return

    valider_transaction(
        session,
        "Évaluation enregistrée.",
    )


def charger_participations_session(
    session: OrmSession,
    session_questionnaire: SessionQuestionnaire,
) -> list[Participation]:
    return list(
        session.scalars(
            select(Participation)
            .where(
                Participation.session_questionnaire_id
                == session_questionnaire.id
            )
            .order_by(Participation.id)
        )
    )


def afficher_rapport(
    rapport: RapportSession,
) -> None:
    statistiques = rapport.statistiques

    afficher_titre("RAPPORT DE SESSION")

    print(
        f"Date de génération          : "
        f"{rapport.date_generation}"
    )
    print(
        f"Participations              : "
        f"{statistiques.nombre_participations}"
    )
    print(
        f"Participations évaluées     : "
        f"{statistiques.nombre_participations_evaluees}"
    )
    print(
        f"Moyenne                     : "
        f"{statistiques.moyenne:.2f}"
    )
    print(
        f"Score minimum               : "
        f"{statistiques.score_minimum}"
    )
    print(
        f"Score maximum               : "
        f"{statistiques.score_maximum}"
    )
    print(
        f"Taux de réussite            : "
        f"{statistiques.taux_reussite:.2f} %"
    )


def consulter_rapport_session(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    sessions = charger_sessions_questionnaire(
        session,
        enseignant,
    )

    session_questionnaire = selectionner_element(
        sessions,
        lambda element: element.nom_session,
        "Session choisie : ",
    )

    if session_questionnaire is None:
        return

    participations = charger_participations_session(
        session,
        session_questionnaire,
    )

    statistiques = (
        StatistiquesSession.genererRapportSession(
            participations
        )
    )

    rapport = RapportSession.generer(statistiques)
    afficher_rapport(rapport)


def cloturer_session(
    session: OrmSession,
    enseignant: Enseignant,
) -> None:
    afficher_titre("CLÔTURE D'UNE SESSION")

    sessions = [
        element
        for element in charger_sessions_questionnaire(
            session,
            enseignant,
        )
        if element.date_debut is not None
        and element.date_fin is None
    ]

    session_questionnaire = selectionner_element(
        sessions,
        lambda element: element.nom_session,
        "Session choisie : ",
    )

    if session_questionnaire is None:
        return

    if not demander_confirmation(
        "Confirmer la clôture de cette session"
    ):
        return

    try:
        session_questionnaire.clore()
    except ValueError as erreur:
        afficher_message_erreur(str(erreur))
        return

    if not valider_transaction(
        session,
        "La session a été clôturée.",
    ):
        return

    participations = charger_participations_session(
        session,
        session_questionnaire,
    )

    statistiques = (
        StatistiquesSession.genererRapportSession(
            participations
        )
    )

    rapport = RapportSession.generer(statistiques)
    afficher_rapport(rapport)


# ============================================================================
# MENUS
# ============================================================================


def afficher_menu_principal() -> None:
    afficher_titre("QUIZZENCLASSE")
    print("1. Se connecter")
    print("2. Créer un compte enseignant")
    print("3. Importer les établissements")
    print("4. Afficher les établissements")
    print("0. Quitter")


def afficher_menu_enseignant(
    enseignant: Enseignant,
) -> None:
    afficher_titre(
        f"ESPACE ENSEIGNANT — "
        f"{enseignant.nom_utilisateur}"
    )
    print("1. Créer un élève")
    print("2. Afficher les élèves")
    print("3. Former une équipe")
    print("4. Afficher les participants")
    print("5. Créer un questionnaire QCM")
    print("6. Afficher les questionnaires")
    print("7. Créer une session de questionnaire")
    print("8. Afficher les sessions")
    print("9. Démarrer une session")
    print("10. Évaluer un participant")
    print("11. Clôturer une session et générer le rapport")
    print("12. Consulter le rapport d'une session")
    print("0. Se déconnecter")


def menu_enseignant(
    session: OrmSession,
    connexion_service: ConnexionService,
    enseignant: Enseignant,
) -> None:
    while True:
        afficher_menu_enseignant(enseignant)

        choix = demander_entier(
            "Votre choix : ",
            minimum=0,
            maximum=12,
        )

        try:
            match choix:
                case 1:
                    creer_eleve(session)

                case 2:
                    afficher_eleves(session)

                case 3:
                    former_equipe(session)

                case 4:
                    afficher_participants(session)

                case 5:
                    creer_questionnaire(
                        session,
                        enseignant,
                    )

                case 6:
                    afficher_questionnaires(
                        session,
                        enseignant,
                    )

                case 7:
                    creer_session_questionnaire(
                        session,
                        enseignant,
                    )

                case 8:
                    afficher_sessions(
                        session,
                        enseignant,
                    )

                case 9:
                    demarrer_session(
                        session,
                        enseignant,
                    )

                case 10:
                    evaluer_participant(
                        session,
                        enseignant,
                    )

                case 11:
                    cloturer_session(
                        session,
                        enseignant,
                    )

                case 12:
                    consulter_rapport_session(
                        session,
                        enseignant,
                    )

                case 0:
                    connexion_service.deconnecter()
                    print("Déconnexion effectuée.")
                    return

        except SQLAlchemyError as erreur:
            session.rollback()
            afficher_message_erreur(str(erreur))

        except (TypeError, ValueError) as erreur:
            session.rollback()
            afficher_message_erreur(str(erreur))


def menu_principal(
    session: OrmSession,
    connexion_service: ConnexionService,
) -> None:
    while True:
        afficher_menu_principal()

        choix = demander_entier(
            "Votre choix : ",
            minimum=0,
            maximum=4,
        )

        match choix:
            case 1:
                enseignant = connecter_enseignant(
                    connexion_service
                )

                if enseignant is not None:
                    menu_enseignant(
                        session,
                        connexion_service,
                        enseignant,
                    )

            case 2:
                inscrire_enseignant(
                    connexion_service
                )

            case 3:
                importer_etablissements(session)

            case 4:
                afficher_etablissements(session)

            case 0:
                print("Fermeture de QuizzenClasse.")
                return


# ============================================================================
# ARGUMENTS TECHNIQUES ET POINT D'ENTRÉE
# ============================================================================


def construire_parseur() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QuizzenClasse : application interactive "
            "en ligne de commande."
        )
    )

    sous_commandes = parser.add_subparsers(
        dest="cmd",
        required=False,
    )

    commande_import = sous_commandes.add_parser(
        "seed-etabs",
        help=(
            "Importer directement les établissements "
            "sans ouvrir le menu."
        ),
    )

    commande_import.add_argument(
        "--csv",
        type=Path,
        default=CHEMIN_CSV_PAR_DEFAUT,
        help="Chemin du fichier CSV.",
    )

    commande_import.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Désactiver la détection des doublons.",
    )

    commande_import.add_argument(
        "--update-on-duplicate",
        action="store_true",
        help="Mettre à jour les établissements existants.",
    )

    return parser


def main() -> int:
    arguments = construire_parseur().parse_args()

    try:
        initialiser_base()
    except SQLAlchemyError as erreur:
        afficher_message_erreur(
            f"Initialisation de la base impossible : {erreur}"
        )
        return 1

    with Session() as session:
        connexion_service = ConnexionService(session)

        if arguments.cmd == "seed-etabs":
            importer_etablissements(
                session,
                arguments.csv,
                dedupe=not arguments.no_dedupe,
                update_on_duplicate=(
                    arguments.update_on_duplicate
                ),
            )
            return 0

        menu_principal(
            session,
            connexion_service,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
