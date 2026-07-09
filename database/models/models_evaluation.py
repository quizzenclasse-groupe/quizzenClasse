# database/models/models_evaluation.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Model
from database.tables_association import eleve_cours, eleve_option

if TYPE_CHECKING:
    from database.models.models_participants import (
        Eleve,
        Equipe,
        Participant,
        Participation,
    )
    from database.models.models_utilisateurs import Enseignant


# ============================================================================
# COURS ET OPTIONS
# ============================================================================


class Cours(Model):
    __tablename__ = "cours"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom_cours: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    enseignant_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    enseignant: Mapped["Enseignant"] = relationship(
        back_populates="cours_enseignes",
    )

    eleves: Mapped[list["Eleve"]] = relationship(
        secondary=eleve_cours,
        back_populates="cours",
    )

    equipes: Mapped[list["Equipe"]] = relationship(
        back_populates="cours",
    )


class Option(Model):
    __tablename__ = "option"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom_option: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    eleves: Mapped[list["Eleve"]] = relationship(
        secondary=eleve_option,
        back_populates="options",
    )


# ============================================================================
# QUESTIONNAIRES, QUESTIONS ET PROPOSITIONS
# ============================================================================


class Questionnaire(Model):
    __tablename__ = "questionnaire"

    id: Mapped[int] = mapped_column(primary_key=True)

    titre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    niveau: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    matiere: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    difficulte: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    date_creation: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    auteur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    auteur: Mapped["Enseignant"] = relationship()

    questions: Mapped[list["Question"]] = relationship(
        back_populates="questionnaire",
        cascade="all, delete-orphan",
    )

    sessions: Mapped[list["SessionQuestionnaire"]] = relationship(
        back_populates="questionnaire",
        cascade="all, delete-orphan",
    )

    def ajouterQuestion(self, question: "Question") -> None:
        if question in self.questions:
            raise ValueError(
                "Cette question appartient déjà au questionnaire."
            )

        self.questions.append(question)


class Question(Model):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)

    questionnaire_id: Mapped[int] = mapped_column(
        ForeignKey("questionnaire.id"),
        nullable=False,
    )

    questionnaire: Mapped["Questionnaire"] = relationship(
        back_populates="questions",
    )

    enonce: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    type_question: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="QCM",
    )

    propositions: Mapped[list["Proposition"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def ajouterProposition(
        self,
        proposition: "Proposition",
    ) -> None:
        if proposition in self.propositions:
            raise ValueError(
                "Cette proposition appartient déjà à la question."
            )

        self.propositions.append(proposition)


class Proposition(Model):
    __tablename__ = "proposition"

    id: Mapped[int] = mapped_column(primary_key=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("question.id"),
        nullable=False,
    )

    question: Mapped["Question"] = relationship(
        back_populates="propositions",
    )

    libelle: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    est_correcte: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )


# ============================================================================
# SESSIONS DE QUESTIONNAIRE
# ============================================================================


class SessionQuestionnaire(Model):
    __tablename__ = "session_questionnaire"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom_session: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="individuel",
    )

    date_debut: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    date_fin: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    questionnaire_id: Mapped[int] = mapped_column(
        ForeignKey("questionnaire.id"),
        nullable=False,
    )

    questionnaire: Mapped["Questionnaire"] = relationship(
        back_populates="sessions",
    )

    participations: Mapped[list["Participation"]] = relationship(
        back_populates="session_questionnaire",
    )

    rapports: Mapped[list["Rapport"]] = relationship(
        back_populates="session",
    )

    @classmethod
    def creer(
        cls,
        questionnaire: Questionnaire,
        titre: str,
        mode: str,
    ) -> "SessionQuestionnaire":
        titre = titre.strip()
        mode = mode.strip()

        if not titre:
            raise ValueError(
                "Le titre de la session est obligatoire."
            )

        if not mode:
            raise ValueError(
                "Le mode de la session est obligatoire."
            )

        return cls(
            questionnaire=questionnaire,
            nom_session=titre,
            mode=mode,
            date_debut=None,
            date_fin=None,
        )

    def lancer(self) -> None:
        if self.date_fin is not None:
            raise ValueError(
                "Une session clôturée ne peut pas être démarrée."
            )

        if self.date_debut is not None:
            raise ValueError(
                "La session a déjà été démarrée."
            )

        self.date_debut = date.today()

    def clore(self) -> None:
        if self.date_debut is None:
            raise ValueError(
                "Une session non démarrée ne peut pas être clôturée."
            )

        if self.date_fin is not None:
            raise ValueError(
                "La session est déjà clôturée."
            )

        self.date_fin = date.today()


# ============================================================================
# RAPPORTS PERSISTANTS
# ============================================================================


class Rapport(Model):
    __tablename__ = "rapport"

    id: Mapped[int] = mapped_column(primary_key=True)

    enseignant_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )

    enseignant: Mapped["Enseignant"] = relationship(
        back_populates="rapports_auteurs",
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("session_questionnaire.id"),
        nullable=False,
    )

    session: Mapped["SessionQuestionnaire"] = relationship(
        back_populates="rapports",
    )

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id"),
        nullable=False,
    )

    participant: Mapped["Participant"] = relationship(
        back_populates="rapports",
    )

    notes: Mapped[list["Note"]] = relationship(
        back_populates="rapport",
        cascade="all, delete-orphan",
    )

    observations: Mapped[list["Observation"]] = relationship(
        back_populates="rapport",
        cascade="all, delete-orphan",
    )

    graphiques: Mapped[list["Graphique"]] = relationship(
        back_populates="rapport",
        cascade="all, delete-orphan",
    )


class Note(Model):
    __tablename__ = "note"

    id: Mapped[int] = mapped_column(primary_key=True)

    rapport_id: Mapped[int] = mapped_column(
        ForeignKey("rapport.id"),
        nullable=False,
    )

    rapport: Mapped["Rapport"] = relationship(
        back_populates="notes",
    )

    valeur: Mapped[float] = mapped_column(
        nullable=False,
    )

    date_evaluation: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )


class Observation(Model):
    __tablename__ = "observation"

    id: Mapped[int] = mapped_column(primary_key=True)

    rapport_id: Mapped[int] = mapped_column(
        ForeignKey("rapport.id"),
        nullable=False,
    )

    rapport: Mapped["Rapport"] = relationship(
        back_populates="observations",
    )

    texte: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )


class Graphique(Model):
    __tablename__ = "graphique"

    id: Mapped[int] = mapped_column(primary_key=True)

    rapport_id: Mapped[int] = mapped_column(
        ForeignKey("rapport.id"),
        nullable=False,
    )

    rapport: Mapped["Rapport"] = relationship(
        back_populates="graphiques",
    )

    reference_fichier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


# ============================================================================
# STATISTIQUES ET RAPPORT DE SESSION
# ============================================================================


@dataclass(frozen=True, slots=True)
class StatistiquesSession:
    nombre_participations: int
    nombre_participations_evaluees: int
    moyenne: float
    score_minimum: float | None
    score_maximum: float | None
    taux_reussite: float

    @staticmethod
    def calculerMoyenneSession(
        participations: Sequence["Participation"],
    ) -> float:
        scores = [
            float(participation.score)
            for participation in participations
            if participation.score is not None
        ]

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    @classmethod
    def genererRapportSession(
        cls,
        participations: Sequence["Participation"],
        *,
        seuil_reussite: float = 5.0,
    ) -> "StatistiquesSession":
        scores = [
            float(participation.score)
            for participation in participations
            if participation.score is not None
        ]

        if not scores:
            return cls(
                nombre_participations=len(participations),
                nombre_participations_evaluees=0,
                moyenne=0.0,
                score_minimum=None,
                score_maximum=None,
                taux_reussite=0.0,
            )

        nombre_reussites = sum(
            score >= seuil_reussite
            for score in scores
        )

        return cls(
            nombre_participations=len(participations),
            nombre_participations_evaluees=len(scores),
            moyenne=sum(scores) / len(scores),
            score_minimum=min(scores),
            score_maximum=max(scores),
            taux_reussite=(
                nombre_reussites / len(scores)
            ) * 100,
        )


@dataclass(frozen=True, slots=True)
class RapportSession:
    statistiques: StatistiquesSession
    date_generation: date

    @classmethod
    def generer(
        cls,
        statistiques: StatistiquesSession,
    ) -> "RapportSession":
        if not isinstance(
            statistiques,
            StatistiquesSession,
        ):
            raise TypeError(
                "Les statistiques doivent être une instance "
                "de StatistiquesSession."
            )

        return cls(
            statistiques=statistiques,
            date_generation=date.today(),
        )
