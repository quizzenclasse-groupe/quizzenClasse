"""
Test fonctionnel manuel de l'API, exécuté avec le TestClient FastAPI
(aucun serveur réseau nécessaire : les requêtes passent directement par
l'application ASGI en mémoire). Sert uniquement de vérification de bout
en bout pendant le développement, PAS une suite pytest formelle.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./quizzenclasse_test.db"

if os.path.exists("quizzenclasse_test.db"):
    os.remove("quizzenclasse_test.db")

from fastapi.testclient import TestClient  # noqa: E402
from api.app import app  # noqa: E402
from database.engine import Session  # noqa: E402
from database.models.models_scolaire import Etablissement  # noqa: E402
import database.models  # noqa: E402,F401

# Le `with` déclenche l'événement "startup" de FastAPI (création des
# tables), exactement comme le ferait un vrai lancement d'uvicorn.
client = TestClient(app)
client.__enter__()

# 1) Etablissement de test (inséré directement, l'import CSV massif reste
#    une opération console d'origine, cf. README "seed-etabs").
s = Session()
etab = Etablissement(
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
s.add(etab)
s.commit()
etab_id = etab.id
s.close()
print("1) etablissement id =", etab_id)

# 2) Inscription enseignant
r = client.post("/api/auth/register", json={
    "nom_utilisateur": "prof_test",
    "mot_de_passe": "motdepasse123",
    "nom": "Dupont", "prenom": "Alice",
})
print("2) register ->", r.status_code, r.json())
assert r.status_code == 201

# 3) Connexion
r = client.post("/api/auth/login-json", json={
    "nom_utilisateur": "prof_test", "mot_de_passe": "motdepasse123",
})
print("3) login ->", r.status_code)
assert r.status_code == 200
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 4) Profil courant
r = client.get("/api/auth/moi", headers=headers)
print("4) moi ->", r.status_code, r.json())
assert r.status_code == 200

# 5) Recherche etablissement
r = client.get("/api/etablissements", params={"q": "Lycee"}, headers=headers)
print("5) recherche etab ->", r.status_code, r.json())
assert r.status_code == 200 and len(r.json()) == 1

# 6) Creation niveau
r = client.post("/api/niveaux", json={
    "nom_niveau": "Terminale S", "etablissement_id": etab_id,
}, headers=headers)
print("6) creer niveau ->", r.status_code, r.json())
assert r.status_code == 201
niveau_id = r.json()["id"]

# 7) Creation eleve
r = client.post("/api/eleves", json={
    "nom": "Martin", "prenom": "Julie",
    "date_naissance": "2008-05-12", "redoublant": False,
    "niveau_ids": [niveau_id],
}, headers=headers)
print("7) creer eleve ->", r.status_code, r.json())
assert r.status_code == 201
eleve_id = r.json()["id"]

# 8) Creation questionnaire avec question + propositions imbriquees
r = client.post("/api/questionnaires", json={
    "titre": "QCM Geographie", "matiere": "Geo", "difficulte": "facile",
    "questions": [{
        "enonce": "Capitale de la France ?",
        "propositions": [
            {"libelle": "Paris", "est_correcte": True},
            {"libelle": "Lyon", "est_correcte": False},
        ],
    }],
}, headers=headers)
print("8) creer questionnaire ->", r.status_code, r.json())
assert r.status_code == 201
questionnaire_id = r.json()["id"]

# 9) Creation session
r = client.post("/api/sessions", json={
    "nom_session": "Session du 12/07", "mode": "individuel",
    "questionnaire_id": questionnaire_id,
}, headers=headers)
print("9) creer session ->", r.status_code, r.json())
assert r.status_code == 201
session_id = r.json()["id"]

# 10) Demarrage session
r = client.post(f"/api/sessions/{session_id}/demarrer", headers=headers)
print("10) demarrer session ->", r.status_code, r.json())
assert r.status_code == 200

# 11) Inscription eleve a la session
r = client.post(f"/api/sessions/{session_id}/participations", json={
    "participant_id": eleve_id,
}, headers=headers)
print("11) inscrire participation ->", r.status_code, r.json())
assert r.status_code == 201
participation_id = r.json()["id"]

# 12) Evaluation
r = client.patch(f"/api/participations/{participation_id}/evaluer", json={
    "score": 8.5, "commentaire_final": "Bon travail",
}, headers=headers)
print("12) evaluer ->", r.status_code, r.json())
assert r.status_code == 200

# 13) Cloture session
r = client.post(f"/api/sessions/{session_id}/cloturer", headers=headers)
print("13) cloturer session ->", r.status_code, r.json())
assert r.status_code == 200

# 14) Statistiques
r = client.get(f"/api/sessions/{session_id}/statistiques", headers=headers)
print("14) statistiques ->", r.status_code, r.json())
assert r.status_code == 200

# 15) Rapport complet
r = client.get(f"/api/sessions/{session_id}/rapport", headers=headers)
print("15) rapport ->", r.status_code, r.json())
assert r.status_code == 200

# 16) Verification du controle des droits : un 2e enseignant ne doit pas
#     pouvoir modifier le questionnaire du premier.
client.post("/api/auth/register", json={
    "nom_utilisateur": "prof_intrus", "mot_de_passe": "autremdp123",
})
r = client.post("/api/auth/login-json", json={
    "nom_utilisateur": "prof_intrus", "mot_de_passe": "autremdp123",
})
token2 = r.json()["access_token"]
headers2 = {"Authorization": f"Bearer {token2}"}
r = client.patch(f"/api/questionnaires/{questionnaire_id}", json={
    "titre": "Piratage"
}, headers=headers2)
print("16) intrusion refusee ->", r.status_code, r.json())
assert r.status_code == 403

# --- Flux public eleve (sans compte) --------------------------------------
# On repart d'une nouvelle session (celle du dessus est deja cloturee).

r = client.post("/api/sessions", json={
    "nom_session": "Session publique", "mode": "individuel",
    "questionnaire_id": questionnaire_id,
}, headers=headers)
session2_id = r.json()["id"]
client.post(f"/api/sessions/{session2_id}/demarrer", headers=headers)

r = client.post(f"/api/sessions/{session2_id}/participations", json={
    "participant_id": eleve_id,
}, headers=headers)
participation2_id = r.json()["id"]

r = client.get(f"/api/sessions/{session2_id}/code-partage", headers=headers)
print("17) recuperer code ->", r.status_code, r.json())
assert r.status_code == 200
code = r.json()["code"]

# Mauvais code refuse
r = client.get(f"/api/public/sessions/{session2_id}/000000")
print("18) mauvais code refuse ->", r.status_code)
assert r.status_code == 403

# Bon code : l'eleve ouvre la session
r = client.get(f"/api/public/sessions/{session2_id}/{code}")
print("19) ouverture publique ->", r.status_code, r.json())
assert r.status_code == 200
donnees_publiques = r.json()
assert donnees_publiques["participants_en_attente"][0]["participation_id"] == participation2_id
# Les bonnes reponses ne doivent JAMAIS être visibles cote eleve.
assert "est_correcte" not in donnees_publiques["questions"][0]["propositions"][0]

id_bonne_proposition = next(
    p["id"] for p in donnees_publiques["questions"][0]["propositions"]
    if p["libelle"] == "Paris"
)

r = client.post(f"/api/public/sessions/{session2_id}/{code}/reponses", json={
    "participation_id": participation2_id,
    "reponses": [{"question_id": donnees_publiques["questions"][0]["id"],
                  "proposition_ids": [id_bonne_proposition]}],
})
print("20) soumission reponses ->", r.status_code, r.json())
assert r.status_code == 200
assert r.json()["score_sur_20"] == 20.0

# Une 2e soumission pour la meme participation doit etre refusee.
r = client.post(f"/api/public/sessions/{session2_id}/{code}/reponses", json={
    "participation_id": participation2_id,
    "reponses": [],
})
print("21) double soumission refusee ->", r.status_code)
assert r.status_code == 409

print("\nTOUS LES TESTS SONT PASSES AVEC SUCCES.")
