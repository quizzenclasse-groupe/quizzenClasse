# api/schemas/session.py
"""
Schémas Pydantic pour les sessions de questionnaire, les participations
(inscriptions + évaluations) et les statistiques/rapports de session.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, computed_field

# ----------------------------------------------------------------------------
# Sessions
# ----------------------------------------------------------------------------


class SessionCreation(BaseModel):
    nom_session: str = Field(min_length=1, max_length=120)
    mode: str = Field(
        default="individuel",
        description='"individuel" ou "equipe", selon le mode de passation.',
    )
    questionnaire_id: int


class SessionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_session: str
    mode: str
    date_debut: date | None = None
    date_fin: date | None = None
    questionnaire_id: int

    @computed_field
    @property
    def statut(self) -> str:
        if self.date_fin is not None:
            return "cloturee"
        if self.date_debut is not None:
            return "en_cours"
        return "planifiee"


# ----------------------------------------------------------------------------
# Participations
# ----------------------------------------------------------------------------


class ParticipationCreation(BaseModel):
    """
    Inscrit un participant (élève OU équipe) à une session.

    Le modèle ORM `Participation` référence un `Participant` générique
    (classe mère commune à `Eleve` et `Equipe` via l'héritage à table
    unique sur la table `participant`) : un seul champ `participant_id`
    suffit donc, quel que soit le type concret.
    """

    participant_id: int
    commentaire_initial: str | None = None


class ParticipationEvaluation(BaseModel):
    """Corps de requête pour noter une participation existante."""

    score: float = Field(ge=0)
    commentaire_final: str | None = None


class ParticipationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_questionnaire_id: int
    participant_id: int
    score: float | None = None
    commentaire_initial: str | None = None
    commentaire_final: str | None = None


# ----------------------------------------------------------------------------
# Statistiques / rapport de session
# ----------------------------------------------------------------------------


class StatistiquesSessionPublic(BaseModel):
    """
    Miroir JSON du dataclass `StatistiquesSession`
    (database/models/models_evaluation.py), qui n'est pas persisté en
    base : il est recalculé à la volée à partir des participations.
    """

    model_config = ConfigDict(from_attributes=True)

    nombre_participations: int
    nombre_participations_evaluees: int
    moyenne: float
    score_minimum: float | None
    score_maximum: float | None
    taux_reussite: float


class RapportSessionPublic(BaseModel):
    """Miroir JSON du dataclass `RapportSession`."""

    model_config = ConfigDict(from_attributes=True)

    statistiques: StatistiquesSessionPublic
    date_generation: date


# ----------------------------------------------------------------------------
# Accès public élève (sans compte) : passation d'un questionnaire
# ----------------------------------------------------------------------------


class PropositionSansReponse(BaseModel):
    """
    Une proposition telle que vue par l'élève : SANS l'indicateur
    `est_correcte`, pour ne pas révéler la bonne réponse avant correction.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str


class QuestionSansReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enonce: str
    propositions: list[PropositionSansReponse] = Field(default_factory=list)


class ParticipantAChoisir(BaseModel):
    """Une entrée de la liste déroulante permettant à l'élève de se désigner."""

    participation_id: int
    nom_affiche: str


class SessionPubliquePourEleve(BaseModel):
    """Ce que voit un élève en ouvrant le lien de la session."""

    nom_session: str
    titre_questionnaire: str
    questions: list[QuestionSansReponse]
    participants_en_attente: list[ParticipantAChoisir]


class ReponseSoumise(BaseModel):
    """Les propositions cochées par l'élève pour une question donnée."""

    question_id: int
    proposition_ids: list[int] = Field(default_factory=list)


class SoumissionReponses(BaseModel):
    """Corps de requête envoyé par l'élève à la fin du questionnaire."""

    participation_id: int
    reponses: list[ReponseSoumise]


class ResultatSoumission(BaseModel):
    """Ce qui est renvoyé à l'élève juste après sa soumission."""

    score_sur_20: float
    nombre_correctes: int
    nombre_questions: int
