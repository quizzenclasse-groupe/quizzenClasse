# database/features/management_ps.py
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.models_utilisateurs import Utilisateur, Enseignant
    from database.models.models_scolaire import Etablissement, NiveauScolaire, ListeEtablissement
    from database.models.models_participants import Eleve, Groupe, BulletinParticipation


class ManagementParcoursScolaire:
    """
    Contrôleur d'orchestration pour l'environnement scolaire.

    Cette classe gère les cas d'usage :
    recherche d'établissement, rattachement de niveau, création et
    modification d'élèves, création de groupes et consultation des bulletins.
    """

    @staticmethod
    def _est_admin(utilisateur: "Utilisateur") -> bool:
        return getattr(utilisateur, "type_utilisateur", None) == "admin"

    def _verifier_droits(
        self,
        utilisateur: "Utilisateur",
        enseignant: "Enseignant",
    ) -> None:
        """
        Autorise l'action si l'utilisateur est admin ou s'il agit sur lui-même.
        """
        if self._est_admin(utilisateur):
            return
        if utilisateur.id == enseignant.id:
            return
        raise PermissionError(
            "Vous ne pouvez agir que sur votre propre environnement scolaire."
        )

    def rechercherEtablissement(
        self,
        nom: str,
        fichier: "ListeEtablissement",
        *,
        nom_academie: str | None = None,
        code_postal: str | None = None,
    ) -> "Etablissement":
        """
        Recherche un établissement dans la liste de référence.

        Cette méthode reste volontairement stricte : si plusieurs résultats
        sont trouvés, le contrôleur d'interface doit demander à l'utilisateur
        de préciser sa sélection.
        """
        resultats = fichier.rechercher(
            nom=nom,
            nom_academie=nom_academie,
            code_postal=code_postal,
        )

        if not resultats:
            raise ValueError("Aucun établissement ne correspond à la recherche.")

        if len(resultats) > 1:
            raise ValueError(
                "Recherche ambiguë : plusieurs établissements correspondent."
            )

        return resultats[0]

    def ajouterEtablissement(
        self,
        e: "Etablissement",
        enseignant: "Enseignant",
        parcours_scolaire_bd: "ParcoursScolaireBD",
        *,
        utilisateur: "Utilisateur | None" = None,
    ) -> None:
        """
        Rattache un établissement à un enseignant.
        """
        acteur = utilisateur or enseignant
        self._verifier_droits(acteur, enseignant)

        enseignant.nom_etablissement = e.getNom()
        parcours_scolaire_bd.sauvegarderEtablissement(
            enseignant_id=enseignant.id,
            etablissement=e,
        )

    def rattacherNiveauScolaire(
        self,
        nom: str,
        e: "Etablissement",
        enseignant: "Enseignant",
        parcours_scolaire_bd: "ParcoursScolaireBD",
        *,
        utilisateur: "Utilisateur | None" = None,
    ) -> "NiveauScolaire":
        """
        Crée un niveau scolaire rattaché à un établissement et à un enseignant.
        """
        acteur = utilisateur or enseignant
        self._verifier_droits(acteur, enseignant)

        niveau = NiveauScolaire(
            nom=nom,
            etablissement_id=e.getId(),
            enseignant_id=enseignant.id,
        )
        parcours_scolaire_bd.sauvegarderNiveauScolaire(niveau)
        return niveau

    def ajouterEleve(
        self,
        nom: str,
        prenom: str,
        date_naissance: date,
        niveau: "NiveauScolaire",
        redoublant: bool,
        parcours_scolaire_bd: "ParcoursScolaireBD",
        **kwargs,
    ) -> "Eleve":
        """
        Ajoute un élève à un niveau scolaire.
        """
        eleve = Eleve.creer(
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            redoublant=redoublant,
            **kwargs,
        )
        niveau.ajouterEleve(eleve)
        parcours_scolaire_bd.sauvegarderEleve(eleve)
        return eleve

    def consulterEleves(
        self,
        niveau: "NiveauScolaire",
        e: "Etablissement",
        parcours_scolaire_bd: "ParcoursScolaireBD",
    ) -> list["Eleve"]:
        """
        Retourne les élèves d'un niveau pour un établissement donné.
        """
        if niveau.getEtablissementId() != e.getId():
            raise ValueError(
                "Le niveau scolaire fourni n'appartient pas à l'établissement demandé."
            )
        return parcours_scolaire_bd.chargerElevesParNiveau(niveau.getId())

    def modifierEleve(
        self,
        eleve_id: int,
        parcours_scolaire_bd: "ParcoursScolaireBD",
        **modifications,
    ) -> None:
        """
        Modifie un élève existant.

        Les champs réellement modifiables sont contrôlés par le modèle `Eleve`.
        """
        eleve = parcours_scolaire_bd.chargerEleve(eleve_id)
        if eleve is None:
            raise ValueError(f"Aucun élève ne correspond à l'identifiant {eleve_id}.")

        eleve.mettre_a_jour(**modifications)
        parcours_scolaire_bd.sauvegarderEleve(eleve)

    def creerGroupe(
        self,
        nom: str,
        eleves: list["Eleve"],
        groupe_bd: "GroupeBD",
    ) -> "Groupe":
        """
        Crée un groupe à partir d'une liste d'élèves.
        """
        groupe = Groupe.creer_depuis_eleves(nom=nom, eleves=eleves)
        groupe_bd.sauvegarder(groupe)
        return groupe

    def consulterBulletin(
        self,
        eleve_id: int,
        bulletin_bd: "BulletinParticipationBD",
    ) -> list["BulletinParticipation"]:
        """
        Retourne les bulletins de participation d'un élève.
        """
        return bulletin_bd.chargerParEleve(eleve_id)
