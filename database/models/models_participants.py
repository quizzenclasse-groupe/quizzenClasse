# database/models/models_participants.py

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Model
from database.tables_association import (
    eleve_cours,
    eleve_option,
    equipe_eleve,
    niveau_eleve,
)

if TYPE_CHECKING:
    from database.models.models_evaluation import (
        Cours,
        Option,
        Rapport,
        SessionQuestionnaire,
    )
    from database.models.models_scolaire import Niveau


class Participant(Model):
    """
    Classe mère des entités pouvant participer à une session :
    un élève ou une équipe.
    """

    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    type_participant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    participations: Mapped[list["Participation"]] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
    )

    rapports: Mapped[list["Rapport"]] = relationship(
        back_populates="participant",
    )

    __mapper_args__ = {
        "polymorphic_on": type_participant,
        "polymorphic_identity": "participant",
    }


class Participation(Model):
    """
    Inscription d'un participant à une session de questionnaire.
    """

    __tablename__ = "participation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_questionnaire_id: Mapped[int] = mapped_column(
        ForeignKey("session_questionnaire.id"),
        nullable=False,
    )

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id"),
        nullable=False,
    )

    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    commentaire_initial: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    commentaire_final: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    participant: Mapped["Participant"] = relationship(
        back_populates="participations",
    )

    session_questionnaire: Mapped["SessionQuestionnaire"] = relationship(
        back_populates="participations",
    )

    def evaluer(
        self,
        score: float,
        commentaire_initial: str | None = None,
        commentaire_final: str | None = None,
    ) -> None:
        if score < 0:
            raise ValueError("Le score ne peut pas être négatif.")

        self.score = score

        if commentaire_initial is not None:
            self.commentaire_initial = commentaire_initial

        if commentaire_final is not None:
            self.commentaire_final = commentaire_final


class Equipe(Participant):
    """
    Groupe d'élèves participant collectivement à une session.
    """

    nom_equipe: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    cours_id: Mapped[int | None] = mapped_column(
        ForeignKey("cours.id"),
        nullable=True,
    )

    cours: Mapped["Cours | None"] = relationship(
        back_populates="equipes",
    )

    membres: Mapped[list["Eleve"]] = relationship(
        secondary=equipe_eleve,
        primaryjoin=lambda: Equipe.id == equipe_eleve.c.equipe_id,
        secondaryjoin=lambda: Eleve.id == equipe_eleve.c.eleve_id,
        back_populates="equipes",
    )

    __mapper_args__ = {
        "polymorphic_identity": "equipe",
    }

    @classmethod
    def creer_depuis_eleves(
        cls,
        nom: str,
        eleves: list["Eleve"],
    ) -> "Equipe":
        nom = nom.strip()

        if not nom:
            raise ValueError("Le nom du groupe est obligatoire.")

        if not eleves:
            raise ValueError(
                "Un groupe doit contenir au moins un élève."
            )

        groupe = cls(nom_equipe=nom)
        groupe.membres.extend(eleves)

        return groupe


# Correspondance avec le vocabulaire retenu dans l'UML.
Groupe = Equipe


class Eleve(Participant):
    """
    Élève susceptible de participer individuellement ou en équipe.
    """

    nom_eleve: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    prenom: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    date_naissance: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    redoublant: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
    )

    ville: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    cp: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    niveaux: Mapped[list["Niveau"]] = relationship(
        secondary=niveau_eleve,
        back_populates="eleves",
    )

    options: Mapped[list["Option"]] = relationship(
        secondary=eleve_option,
        back_populates="eleves",
    )

    cours: Mapped[list["Cours"]] = relationship(
        secondary=eleve_cours,
        back_populates="eleves",
    )

    equipes: Mapped[list["Equipe"]] = relationship(
        secondary=equipe_eleve,
        primaryjoin=lambda: Eleve.id == equipe_eleve.c.eleve_id,
        secondaryjoin=lambda: Equipe.id == equipe_eleve.c.equipe_id,
        back_populates="membres",
    )

    __mapper_args__ = {
        "polymorphic_identity": "eleve",
    }

    @classmethod
    def creer(
        cls,
        nom: str,
        prenom: str,
        date_naissance: date | None,
        redoublant: bool,
        **kwargs,
    ) -> "Eleve":
        nom = nom.strip()
        prenom = prenom.strip()

        if not nom:
            raise ValueError(
                "Le nom de l'élève est obligatoire."
            )

        if not prenom:
            raise ValueError(
                "Le prénom de l'élève est obligatoire."
            )

        return cls(
            nom_eleve=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            redoublant=redoublant,
            **kwargs,
        )

    def mettre_a_jour(self, **modifications) -> None:
        champs_autorises = {
            "nom_eleve",
            "prenom",
            "date_naissance",
            "redoublant",
            "ville",
            "cp",
        }

        for cle, valeur in modifications.items():
            if cle in champs_autorises and valeur is not None:
                setattr(self, cle, valeur)


class BulletinParticipation(Model):
    __tablename__ = "bulletin_participation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    eleve_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id"),
        nullable=False,
    )

    appreciation: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    eleve: Mapped["Eleve"] = relationship()

    @classmethod
    def depuis_participations(
        cls,
        eleve_id: int,
        participations: list["Participation"],
    ) -> list["BulletinParticipation"]:
        return [
            cls(
                eleve_id=eleve_id,
                appreciation=(
                    f"Score={participation.score}, "
                    f"commentaire initial="
                    f"{participation.commentaire_initial}, "
                    f"commentaire final="
                    f"{participation.commentaire_final}"
                ),
            )
            for participation in participations
        ]