from database.engine import Session
from database.models.models_scolaire import Etablissement
import database.models  # noqa

s = Session()
existe = s.query(Etablissement).filter_by(code_uai="TEST001").first()
if existe is None:
    e = Etablissement(
        nom_etablissement="Lycee Test",
        statut_public_prive="Public",
        adresse_1="1 rue de Test",
        code_departement="75",
        nom_departement="Paris",
        code_uai="TEST001",
        nom_academie="Paris",
        code_postal="75000",
        type_etablissement="etablissement",
    )
    s.add(e)
    s.commit()
    print("etablissement cree, id:", e.id)
else:
    print("etablissement deja present, id:", existe.id)
