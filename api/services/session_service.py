# api/services/session_service.py
"""
Services métier pour les sessions de questionnaire, les participations
et les statistiques/rapports qui en découlent.

Note sur les droits : le modèle `SessionQuestionnaire` ne porte pas de
colonne `enseignant_id` (une session est rattachée à un `Questionnaire`,
qui lui porte `auteur_id`). Le contrôle de droits sur une session est
donc fait via `session.questionnaire.auteur_id`, contrairement à ce que
supposait `database/features/management_quest.py::_verifier_droits_sur_session`
(qui cherchait un `session.enseignant_id` inexistant dans le modèle
actuel) — c'est exactement le type de "légère différence" mentionnée
pour ce projet par rapport à Quiz_app.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from api.repositories.questionnaire_repository import QuestionnaireRepository
from api.repositories.scolaire_repository import EleveRepository, EquipeRepository
from api.repositories.session_repository import (
    ParticipationRepository,
    SessionQuestionnaireRepository,
)
from api.schemas.session import ParticipationCreation, ParticipationEvaluation, SessionCreation
from api.schemas.session import ResultatSoumission, SoumissionReponses, ParticipantAChoisir
from api.schemas.session import QuestionSansReponse, SessionPubliquePourEleve
from api.security import code_acces_session, est_admin, verifier_code_session
from database.models.models_evaluation import (
    RapportSession,
    SessionQuestionnaire,
    StatistiquesSession,
)
from database.models.models_participants import Participant, Participation
from database.models.models_utilisateurs import Utilisateur


class SessionService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = SessionQuestionnaireRepository(session)
        self.questionnaires = QuestionnaireRepository(session)

    def _verifier_droits(self, session_q: SessionQuestionnaire, utilisateur: Utilisateur) -> None:
        if est_admin(utilisateur):
            return
        if session_q.questionnaire.auteur_id != utilisateur.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez agir que sur vos propres sessions.",
            )

    def obtenir(self, session_id: int) -> SessionQuestionnaire:
        session_q = self.repo.obtenir(session_id)
        if session_q is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable."
            )
        return session_q

    def obtenir_pour(self, session_id: int, utilisateur: Utilisateur) -> SessionQuestionnaire:
        """
        Variante de `obtenir` qui vérifie aussi les droits, utilisée par
        l'endpoint de lecture directe GET /api/sessions/{id} (ajouté pour
        permettre au frontend d'afficher le statut courant d'une session
        sans devoir repasser par la liste des sessions du questionnaire).
        """
        session_q = self.obtenir(session_id)
        self._verifier_droits(session_q, utilisateur)
        return session_q

    def lister_par_questionnaire(
        self, questionnaire_id: int, utilisateur: Utilisateur
    ) -> list[SessionQuestionnaire]:
        questionnaire = self.questionnaires.obtenir(questionnaire_id)
        if questionnaire is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire introuvable.",
            )
        if not est_admin(utilisateur) and questionnaire.auteur_id != utilisateur.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez consulter que vos propres questionnaires.",
            )
        return self.repo.par_questionnaire(questionnaire_id)

    def creer(self, donnees: SessionCreation, enseignant: Utilisateur) -> SessionQuestionnaire:
        questionnaire = self.questionnaires.obtenir(donnees.questionnaire_id)
        if questionnaire is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Questionnaire introuvable.",
            )
        if not est_admin(enseignant) and questionnaire.auteur_id != enseignant.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez créer une session que pour vos propres questionnaires.",
            )

        try:
            # Réutilisation de la factory métier `SessionQuestionnaire.creer`.
            session_q = SessionQuestionnaire.creer(
                questionnaire=questionnaire,
                titre=donnees.nom_session,
                mode=donnees.mode,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        return self.repo.ajouter(session_q)

    def demarrer(self, session_id: int, utilisateur: Utilisateur) -> SessionQuestionnaire:
        session_q = self.obtenir(session_id)
        self._verifier_droits(session_q, utilisateur)
        try:
            session_q.lancer()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return self.repo.sauvegarder(session_q)

    def cloturer(self, session_id: int, utilisateur: Utilisateur) -> SessionQuestionnaire:
        session_q = self.obtenir(session_id)
        self._verifier_droits(session_q, utilisateur)
        try:
            session_q.clore()
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return self.repo.sauvegarder(session_q)

    def obtenir_code_partage(self, session_id: int, utilisateur: Utilisateur) -> str:
        """
        Renvoie le code d'accès public à transmettre aux élèves (cf.
        `api/security.py::code_acces_session`). Réservé à l'enseignant
        propriétaire (ou à un admin) : le code n'est pas secret une fois
        distribué aux élèves, mais seul le propriétaire de la session
        doit pouvoir le récupérer depuis l'application.
        """
        session_q = self.obtenir(session_id)
        self._verifier_droits(session_q, utilisateur)
        return code_acces_session(session_id)


class ParticipationService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = ParticipationRepository(session)
        self.sessions = SessionQuestionnaireRepository(session)
        self.eleves = EleveRepository(session)
        self.equipes = EquipeRepository(session)

    def _verifier_droits_session(
        self, session_q: SessionQuestionnaire, utilisateur: Utilisateur
    ) -> None:
        if est_admin(utilisateur):
            return
        if session_q.questionnaire.auteur_id != utilisateur.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez agir que sur vos propres sessions.",
            )

    def lister_par_session(self, session_id: int, utilisateur: Utilisateur) -> list[Participation]:
        session_q = self.sessions.obtenir(session_id)
        if session_q is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable."
            )
        self._verifier_droits_session(session_q, utilisateur)
        return self.repo.par_session(session_id)

    def inscrire(
        self, session_id: int, donnees: ParticipationCreation, utilisateur: Utilisateur
    ) -> Participation:
        session_q = self.sessions.obtenir(session_id)
        if session_q is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable."
            )
        self._verifier_droits_session(session_q, utilisateur)

        participant = self.session.get(Participant, donnees.participant_id)
        if participant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Le participant indiqué (élève ou équipe) n'existe pas.",
            )

        if self.repo.existe_deja(session_id, donnees.participant_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce participant est déjà inscrit à cette session.",
            )

        participation = Participation(
            session_questionnaire_id=session_id,
            participant_id=donnees.participant_id,
            commentaire_initial=donnees.commentaire_initial,
        )
        return self.repo.ajouter(participation)

    def evaluer(
        self,
        participation_id: int,
        donnees: ParticipationEvaluation,
        utilisateur: Utilisateur,
    ) -> Participation:
        participation = self.repo.obtenir(participation_id)
        if participation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participation introuvable.",
            )
        self._verifier_droits_session(participation.session_questionnaire, utilisateur)

        try:
            # Réutilisation de la méthode métier `Participation.evaluer`,
            # qui refuse déjà un score négatif.
            participation.evaluer(
                score=donnees.score,
                commentaire_final=donnees.commentaire_final,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        return self.repo.sauvegarder(participation)


class RapportService:
    """
    Calcule les statistiques et le rapport d'une session à la volée
    (aucune table dédiée : `StatistiquesSession` et `RapportSession` sont
    des dataclasses non persistées, cf. models_evaluation.py).
    """

    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.sessions = SessionQuestionnaireRepository(session)
        self.participations = ParticipationRepository(session)

    def _charger_session_autorisee(
        self, session_id: int, utilisateur: Utilisateur
    ) -> SessionQuestionnaire:
        session_q = self.sessions.obtenir(session_id)
        if session_q is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable."
            )
        if not est_admin(utilisateur) and session_q.questionnaire.auteur_id != utilisateur.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez consulter que le rapport de vos propres sessions.",
            )
        return session_q

    def statistiques(self, session_id: int, utilisateur: Utilisateur) -> StatistiquesSession:
        self._charger_session_autorisee(session_id, utilisateur)
        participations = self.participations.par_session(session_id)
        return StatistiquesSession.genererRapportSession(participations)

    def rapport(self, session_id: int, utilisateur: Utilisateur) -> RapportSession:
        stats = self.statistiques(session_id, utilisateur)
        return RapportSession.generer(stats)


class ParticipationPubliqueService:
    """
    Service dédié à l'accès PUBLIC (sans authentification) permettant à
    un élève de répondre à un questionnaire depuis son propre appareil.

    Absent du projet d'origine (aucun compte élève n'existe dans le
    modèle de données), ce service ne crée pas de nouveau mécanisme
    d'authentification : il s'appuie sur un code court dérivé de
    l'identifiant de session (cf. `api/security.py::code_acces_session`)
    et sur les participations déjà inscrites par l'enseignant. L'élève
    ne fait que se désigner dans la liste des participants en attente,
    répondre, puis la note est calculée automatiquement et enregistrée
    via `Participation.evaluer` (méthode déjà existante sur le modèle).
    """

    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.sessions = SessionQuestionnaireRepository(session)
        self.participations = ParticipationRepository(session)

    def _charger_session_publique(self, session_id: int, code: str) -> SessionQuestionnaire:
        session_q = self.sessions.obtenir(session_id)
        if session_q is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable."
            )
        if not verifier_code_session(session_id, code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Code d'accès incorrect.",
            )
        if session_q.date_debut is None or session_q.date_fin is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette session n'est pas ouverte aux réponses actuellement "
                "(pas encore démarrée, ou déjà clôturée par l'enseignant).",
            )
        return session_q

    def obtenir_pour_eleve(self, session_id: int, code: str) -> SessionPubliquePourEleve:
        session_q = self._charger_session_publique(session_id, code)
        questionnaire = session_q.questionnaire

        participations = self.participations.par_session(session_id)
        en_attente = [p for p in participations if p.score is None]

        participants = [
            ParticipantAChoisir(
                participation_id=p.id,
                nom_affiche=(
                    f"{p.participant.prenom} {p.participant.nom_eleve}"
                    if hasattr(p.participant, "nom_eleve") and p.participant.nom_eleve
                    else f"{getattr(p.participant, 'nom_equipe', None) or 'Participant'} #{p.participant_id}"
                ),
            )
            for p in en_attente
        ]

        return SessionPubliquePourEleve(
            nom_session=session_q.nom_session,
            titre_questionnaire=questionnaire.titre,
            questions=[QuestionSansReponse.model_validate(q) for q in questionnaire.questions],
            participants_en_attente=participants,
        )

    def soumettre(
        self, session_id: int, code: str, donnees: SoumissionReponses
    ) -> ResultatSoumission:
        session_q = self._charger_session_publique(session_id, code)
        questionnaire = session_q.questionnaire

        participation = self.participations.obtenir(donnees.participation_id)
        if participation is None or participation.session_questionnaire_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participation introuvable pour cette session.",
            )
        if participation.score is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce participant a déjà répondu à ce questionnaire.",
            )

        # Correction automatique : une question est "correcte" si l'ensemble
        # des propositions cochées par l'élève correspond EXACTEMENT à
        # l'ensemble des propositions marquées `est_correcte` en base
        # (aucun oubli, aucune coche en trop).
        reponses_par_question = {r.question_id: set(r.proposition_ids) for r in donnees.reponses}

        nombre_correctes = 0
        for question in questionnaire.questions:
            attendu = {p.id for p in question.propositions if p.est_correcte}
            fourni = reponses_par_question.get(question.id, set())
            if fourni == attendu:
                nombre_correctes += 1

        nombre_questions = len(questionnaire.questions) or 1
        score_sur_20 = round((nombre_correctes / nombre_questions) * 20, 2)

        participation.evaluer(score=score_sur_20, commentaire_final="Correction automatique")
        self.participations.sauvegarder(participation)

        return ResultatSoumission(
            score_sur_20=score_sur_20,
            nombre_correctes=nombre_correctes,
            nombre_questions=len(questionnaire.questions),
        )
