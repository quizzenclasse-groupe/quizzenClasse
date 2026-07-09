from typing import Sequence, Optional 
from sqlalchemy.orm import Session 
from sqlalchemy import select
from database.models.models_utilisateurs import Enseignant 
from database.models.models_participants import Eleve 
from database.models.models_scolaire import Niveau
from database.services.auth import create_user


def ajouter_enseignant( 
    s: Session, 
    nom: str, 
    email: str, 
    password: str, # 🚨 AJOUT DU MOT DE PASSE À LA SIGNATURE
    role: str = "enseignant" 
) -> int: 
    """ Crée un nouvel Enseignant en utilisant la logique d'authentification. """
    
    # Utiliser create_user pour gérer le hachage et le STI (Single Table Inheritance)
    return create_user(
        s=s,
        email=email,
        password=password,
        nom=nom,
        role=role
    )

    

def creer_eleve( s: Session, nom: str, prenom: str, niveau_ids: Sequence[int], **kwargs ) -> int: 
    """ Crée un nouvel Eleve et l'associe aux Niveaux spécifiés via la relation Many-to-Many.

    Args:
        s: La session SQLAlchemy ouverte.
        nom: Le nom de l'élève.
        prenom: Le prénom de l'élève.
        niveau_ids: Une séquence d'IDs de Niveau (pour la relation M-t-M).
        kwargs: Autres attributs de l'élève (date_naissance, ville, cp, etc.).
        
    Returns:
        L'ID de l'élève créé.
    """

    # 1. Récupérer les objets Niveau correspondants aux IDs
    niveaux_selectionnes = s.scalars(
        select(Niveau).where(Niveau.id.in_(niveau_ids))
    ).all()

    if len(niveaux_selectionnes) != len(niveau_ids):
        # Logique métier : S'assurer que tous les niveaux existent
        raise ValueError("Un ou plusieurs Niveau(x) spécifié(s) n'existe(nt) pas.")

    # 2. Création de l'objet Eleve
    nouvel_eleve = Eleve(
        nom_eleve=nom,
        prenom=prenom,
        niveaux=niveaux_selectionnes, # Assigne la liste d'objets Niveau à la relation M-t-M
        **kwargs
        # L'id du Participant et le discriminateur sont gérés automatiquement
    )

    # 3. Ajout et persistance (le M-t-M est géré par SQLAlchemy ici)
    s.add(nouvel_eleve)
    s.commit()
    s.refresh(nouvel_eleve)

    return nouvel_eleve.id