# api/services/scolaire_service.py
"""
Services métier pour le parcours scolaire : établissements (lecture
seule côté API), niveaux, élèves et équipes.

Chaque méthode qui modifie une ressource commence par vérifier que
l'enseignant courant est bien le propriétaire de la ressource (ou un
administrateur) — c'est la même règle que celle esquissée dans
`database/features/management_ps.py::_verifier_droits`, mais réécrite
ici pour coller aux noms réels des modèles actuels (`Niveau`, et non
`NiveauScolaire` comme l'ancien fichier le supposait) et pour être
directement appelable depuis un endpoint FastAPI.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from api.repositories.scolaire_repository import (
    EleveRepository,
    EquipeRepository,
    EtablissementRepository,
    NiveauRepository,
)
from api.schemas.scolaire import (
    EleveCreation,
    EleveMiseAJour,
    EquipeCreation,
    NiveauCreation,
    NiveauMiseAJour,
)
from api.security import est_admin
from database.models.models_participants import Eleve, Equipe
from database.models.models_scolaire import Etablissement, Niveau
from database.models.models_utilisateurs import Utilisateur


def _verifier_proprietaire(utilisateur: Utilisateur, proprietaire_id: int, ressource: str) -> None:
    """
    Vérification de droits générique et réutilisable : un enseignant ne
    peut agir que sur ses propres ressources, un admin peut tout faire.
    """
    if est_admin(utilisateur):
        return
    if utilisateur.id != proprietaire_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Vous ne pouvez agir que sur vos propres {ressource}.",
        )


class EtablissementService:
    def __init__(self, session: OrmSession) -> None:
        self.repo = EtablissementRepository(session)

    def rechercher(self, terme: str) -> list[Etablissement]:
        if not terme or not terme.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le terme de recherche ne peut pas être vide.",
            )
        return self.repo.rechercher_par_nom(terme)

    def obtenir(self, etablissement_id: int) -> Etablissement:
        etablissement = self.repo.obtenir(etablissement_id)
        if etablissement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Établissement introuvable.",
            )
        return etablissement


class NiveauService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = NiveauRepository(session)
        self.etablissements = EtablissementRepository(session)

    def lister_pour(self, enseignant: Utilisateur) -> list[Niveau]:
        if est_admin(enseignant):
            return self.repo.lister()
        return self.repo.par_enseignant(enseignant.id)

    def obtenir(self, niveau_id: int) -> Niveau:
        niveau = self.repo.obtenir(niveau_id)
        if niveau is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Niveau introuvable."
            )
        return niveau

    def creer(self, donnees: NiveauCreation, enseignant: Utilisateur) -> Niveau:
        if self.etablissements.obtenir(donnees.etablissement_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="L'établissement indiqué n'existe pas.",
            )

        niveau = Niveau(
            nom_niveau=donnees.nom_niveau.strip(),
            etablissement_id=donnees.etablissement_id,
            enseignant_id=enseignant.id,
            effectif=0,
        )
        return self.repo.ajouter(niveau)

    def renommer(
        self, niveau_id: int, donnees: NiveauMiseAJour, enseignant: Utilisateur
    ) -> Niveau:
        niveau = self.obtenir(niveau_id)
        _verifier_proprietaire(enseignant, niveau.enseignant_id, "niveaux")

        # Réutilisation du setter métier existant, qui valide déjà
        # qu'un nom vide est refusé (cf. `Niveau.setNom`).
        try:
            niveau.setNom(donnees.nom_niveau)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        return self.repo.sauvegarder(niveau)

    def supprimer(self, niveau_id: int, enseignant: Utilisateur) -> None:
        niveau = self.obtenir(niveau_id)
        _verifier_proprietaire(enseignant, niveau.enseignant_id, "niveaux")
        self.repo.supprimer(niveau)


class EleveService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = EleveRepository(session)
        self.niveaux = NiveauRepository(session)

    def lister_par_niveau(self, niveau_id: int, enseignant: Utilisateur) -> list[Eleve]:
        niveau = self.niveaux.obtenir(niveau_id)
        if niveau is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Niveau introuvable."
            )
        _verifier_proprietaire(enseignant, niveau.enseignant_id, "niveaux")
        return self.repo.par_niveau(niveau_id)

    def obtenir(self, eleve_id: int) -> Eleve:
        eleve = self.repo.obtenir(eleve_id)
        if eleve is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Élève introuvable."
            )
        return eleve

    def creer(self, donnees: EleveCreation, enseignant: Utilisateur) -> Eleve:
        niveaux = [self.niveaux.obtenir(nid) for nid in donnees.niveau_ids]
        if any(n is None for n in niveaux):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Un ou plusieurs niveaux indiqués n'existent pas.",
            )
        for niveau in niveaux:
            _verifier_proprietaire(enseignant, niveau.enseignant_id, "niveaux")

        try:
            # Réutilisation de la factory métier `Eleve.creer`, qui
            # valide déjà que le nom et le prénom sont non vides.
            eleve = Eleve.creer(
                nom=donnees.nom,
                prenom=donnees.prenom,
                date_naissance=donnees.date_naissance,
                redoublant=donnees.redoublant,
                ville=donnees.ville,
                cp=donnees.cp,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        eleve.niveaux = niveaux
        return self.repo.ajouter(eleve)

    def modifier(
        self, eleve_id: int, donnees: EleveMiseAJour, enseignant: Utilisateur
    ) -> Eleve:
        eleve = self.obtenir(eleve_id)
        # Un élève peut appartenir à plusieurs niveaux : on autorise la
        # modification si l'enseignant est propriétaire d'AU MOINS un
        # des niveaux de l'élève (ou est admin).
        if not est_admin(enseignant) and not any(
            n.enseignant_id == enseignant.id for n in eleve.niveaux
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne gérez aucun niveau de cet élève.",
            )

        modifications = {
            "nom_eleve": donnees.nom,
            "prenom": donnees.prenom,
            "date_naissance": donnees.date_naissance,
            "redoublant": donnees.redoublant,
            "ville": donnees.ville,
            "cp": donnees.cp,
        }
        # `Eleve.mettre_a_jour` ignore déjà les valeurs `None`.
        eleve.mettre_a_jour(**modifications)
        return self.repo.sauvegarder(eleve)


class EquipeService:
    def __init__(self, session: OrmSession) -> None:
        self.session = session
        self.repo = EquipeRepository(session)
        self.eleves = EleveRepository(session)

    def creer(self, donnees: EquipeCreation, enseignant: Utilisateur) -> Equipe:
        membres = self.eleves.par_ids(donnees.eleve_ids)
        if len(membres) != len(donnees.eleve_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Un ou plusieurs élèves indiqués n'existent pas.",
            )

        try:
            # Réutilisation de la factory métier `Equipe.creer_depuis_eleves`.
            equipe = Equipe.creer_depuis_eleves(nom=donnees.nom_equipe, eleves=membres)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc

        equipe.cours_id = donnees.cours_id
        return self.repo.ajouter(equipe)

    def obtenir(self, equipe_id: int) -> Equipe:
        equipe = self.repo.obtenir(equipe_id)
        if equipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Équipe introuvable."
            )
        return equipe
