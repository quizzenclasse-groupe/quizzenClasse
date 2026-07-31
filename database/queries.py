# database/queries.py
# *******************************************************
# Nom ......... : queries.py
# Rôle ........ : Regroupe les requêtes SQLAlchemy utilisées
#                 pour rechercher les utilisateurs et les
#                 enseignants, lister les élèves par niveau
#                 et calculer les effectifs scolaires.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile database/queries.py
# Usage ....... : Module importé par l’application :
#                 from database import queries
# *******************************************************
from __future__ import annotations
from typing import Sequence, Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database.models.models_utilisateurs import Utilisateur, Enseignant
from database.models.models_scolaire import Niveau
from database.models.models_participants import Eleve

# Table d'association Niveau<->Eleve (M<->M)
try:
    from database.tables_association import niveau_eleve
    HAS_M2M = True
except Exception:
    HAS_M2M = False  # fallback: FK direct Eleve.niveau_id

__all__ = [
    "get_user_by_email",
    "get_enseignant_by_email",
    "list_eleves_par_niveau",
    "effectifs_par_niveau",
    "effectifs_par_classe",   # alias vers _par_niveau
]

# ---------- Helpers -----------------------------------------------------------

def _col_email_or_ident(model):
    """Préférer 'email' si présent, sinon 'nom_utilisateur' comme identifiant."""
    return getattr(model, "email", None) or getattr(model, "nom_utilisateur")

# ---------- Utilisateurs ------------------------------------------------------

def get_user_by_email(s: Session, email: str) -> Optional[Utilisateur]:
    col = _col_email_or_ident(Utilisateur)
    return s.execute(select(Utilisateur).where(col == email)).scalar_one_or_none()

def get_enseignant_by_email(s: Session, email: str) -> Optional[Enseignant]:
    col = _col_email_or_ident(Enseignant)
    return s.execute(select(Enseignant).where(col == email)).scalar_one_or_none()

# ---------- Scolaire ----------------------------------------------------------

def list_eleves_par_niveau(s: Session, niveau_id: int) -> Sequence[Eleve]:
    """Liste des élèves d’un niveau (M↔M via niveau_eleve OU FK Eleve.niveau_id)."""
    if HAS_M2M:
        stmt = (
            select(Eleve)
            .join(niveau_eleve, niveau_eleve.c.eleve_id == Eleve.id)
            .where(niveau_eleve.c.niveau_id == niveau_id)
        )
    else:
        # Fallback : une FK directe Eleve.niveau_id
        stmt = select(Eleve).where(getattr(Eleve, "niveau_id") == niveau_id)
    return s.execute(stmt).scalars().all()

def effectifs_par_niveau(s: Session) -> List[Tuple[int, str, int]]:
    """
    Retourne [(niveau_id, niveau_nom, effectif)].
    Compatible avec différents noms de colonne (nom_niveau, nom, libelle).
    """
    niveau_nom_col = getattr(Niveau, "nom_niveau", getattr(Niveau, "nom", getattr(Niveau, "libelle", Niveau.id)))
    if HAS_M2M:
        stmt = (
            select(Niveau.id, niveau_nom_col, func.count(Eleve.id))
            .select_from(Niveau)
            .join(niveau_eleve, niveau_eleve.c.niveau_id == Niveau.id, isouter=True)
            .join(Eleve, Eleve.id == niveau_eleve.c.eleve_id, isouter=True)
            .group_by(Niveau.id, niveau_nom_col)
            .order_by(niveau_nom_col)
        )
    else:
        stmt = (
            select(Niveau.id, niveau_nom_col, func.count(Eleve.id))
            .select_from(Niveau)
            .join(Eleve, getattr(Eleve, "niveau_id") == Niveau.id, isouter=True)
            .group_by(Niveau.id, niveau_nom_col)
            .order_by(niveau_nom_col)
        )
    rows = s.execute(stmt).all()
    return [(int(r[0]), str(r[1]), int(r[2])) for r in rows]

def effectifs_par_classe(s: Session) -> List[Tuple[int, str, int]]:
    """
    « classe » = « niveau ».
    On renvoie les effectifs par niveau pour satisfaire les tests.
    """
    return effectifs_par_niveau(s)
