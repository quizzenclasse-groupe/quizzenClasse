# api/repositories/scolaire_repository.py
# Rôle : Accès à la base de données pour Etablissement, Niveau, Eleve et Equipe.
# Auteur : Fatima Chokri -  ID 190 11 768
# Version : V1
# Date : Juin 2026
# Licence : L2 Projet Réalisation de programme - M. Kislin


from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from api.repositories.base import BaseRepository
from database.models.models_participants import Eleve, Equipe
from database.models.models_scolaire import Etablissement, Niveau


class EtablissementRepository(BaseRepository[Etablissement]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Etablissement)

    def rechercher_par_nom(self, terme: str) -> list[Etablissement]:
        """Recherche simple (LIKE) utilisée par l'endpoint de recherche d'établissement."""
        motif = f"%{terme.strip()}%"
        return list(
            self.session.execute(
                select(Etablissement).where(
                    Etablissement.nom_etablissement.ilike(motif)
                ).limit(25)
            ).scalars().all()
        )


class NiveauRepository(BaseRepository[Niveau]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Niveau)

    def par_enseignant(self, enseignant_id: int) -> list[Niveau]:
        return list(
            self.session.execute(
                select(Niveau).where(Niveau.enseignant_id == enseignant_id)
            ).scalars().all()
        )


class EleveRepository(BaseRepository[Eleve]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Eleve)

    def par_niveau(self, niveau_id: int) -> list[Eleve]:
        niveau = self.session.get(Niveau, niveau_id)
        return list(niveau.eleves) if niveau else []

    def par_ids(self, ids: list[int]) -> list[Eleve]:
        return list(
            self.session.execute(
                select(Eleve).where(Eleve.id.in_(ids))
            ).scalars().all()
        )


class EquipeRepository(BaseRepository[Equipe]):
    def __init__(self, session: OrmSession) -> None:
        super().__init__(session, Equipe)

    def par_cours(self, cours_id: int) -> list[Equipe]:
        return list(
            self.session.execute(
                select(Equipe).where(Equipe.cours_id == cours_id)
            ).scalars().all()
        )
