# QuizzenClasse

## Présentation

**QuizzenClasse** est une application Python en ligne de commande destinée à la gestion de questionnaires pédagogiques.

L’application permet notamment :

* la création et l’authentification d’un compte enseignant ;
* le rattachement d’un enseignant à un établissement ;
* la gestion des niveaux scolaires ;
* la création et l’affectation des élèves ;
* la constitution d’équipes ;
* la création de questionnaires à choix multiples ;
* la création et le suivi de sessions de questionnaire ;
* l’évaluation des participants ;
* le calcul des statistiques ;
* la génération de rapports de session.

Le projet utilise **Python**, **SQLAlchemy 2**, **SQLite** et **pytest**.

---

## Prérequis

Le projet nécessite :

* Python 3.11 ou une version compatible ;
* `pyenv` ;
* `pyenv-virtualenv` ;
* Git ;
* les dépendances Python du projet.

Vérifier la version de Python :

```bash
python --version
```

Vérifier l’installation de Git :

```bash
git --version
```

---

## Récupération du projet

Cloner le dépôt GitHub :

```bash
git clone URL_DU_DEPOT_GITHUB
```

Se placer dans le répertoire du projet :

```bash
cd quizzenClasse
```

Remplacer `URL_DU_DEPOT_GITHUB` par l’adresse réelle du dépôt privé.

L’accès au dépôt nécessite d’avoir préalablement accepté l’invitation envoyée par l’administrateur du projet.

---

## Activation de l’environnement virtuel

L’environnement virtuel utilisé pour le projet est :

```text
standalone-sqlalchemy
```

L’activer avec :

```bash
pyenv activate standalone-sqlalchemy
```

Vérifier l’environnement utilisé :

```bash
pyenv version
```

La sortie doit contenir :

```text
standalone-sqlalchemy
```

Vérifier l’interpréteur Python réellement utilisé :

```bash
python -c "import sys; print(sys.executable)"
```

Le chemin attendu est similaire à :

```text
/home/UTILISATEUR/.pyenv/versions/standalone-sqlalchemy/bin/python
```

---

## Installation des dépendances

Lorsque le fichier `requirements.txt` est présent, installer les dépendances avec :

```bash
python -m pip install -r requirements.txt
```

Vérifier l’installation de SQLAlchemy :

```bash
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Vérifier l’installation de pytest :

```bash
python -m pytest --version
```

---

## Initialisation de la base de données

L’application utilise une base SQLite.

Les tables absentes sont créées automatiquement au lancement du programme.

L’import des établissements peut être exécuté avec :

```bash
python main.py seed-etabs
```

Le fichier utilisé par défaut est :

```text
data/raw/education/fr-en-annuaire-education.csv
```

Lorsque les établissements sont déjà présents dans la base, la commande peut afficher :

```text
OK : 0 établissement(s) importé(s)
```

Ce résultat signifie qu’aucun nouvel établissement n’a été ajouté.

---

## Lancement des tests

Avant toute modification importante ou tout envoi sur GitHub, exécuter l’ensemble des tests :

```bash
python -m pytest -v
```

La suite comprend :

* les tests unitaires ;
* les tests d’intégration ;
* les tests de contrat ;
* le test fonctionnel complet.

### Lancer uniquement les tests unitaires

```bash
python -m pytest tests/unit -v
```

### Lancer uniquement les tests d’intégration

```bash
python -m pytest tests/integration -v
```

### Lancer uniquement les tests de contrat

```bash
python -m pytest tests/contract -v
```

### Lancer uniquement le scénario fonctionnel

```bash
python -m pytest tests/functional -v
```

Le développement ne doit être envoyé sur le dépôt distant qu’après vérification des résultats obtenus.

---

## Lancement de l’application

Lancer le programme principal avec :

```bash
python main.py
```

Le menu principal permet :

```text
1. Se connecter
2. Créer un compte enseignant
3. Importer les établissements
4. Afficher les établissements
0. Quitter
```

Après authentification, l’enseignant accède aux fonctions de gestion du parcours scolaire, des élèves, des questionnaires, des sessions et des rapports.

---

## Lancer les tests puis le programme

Pour lancer l’application uniquement lorsque tous les tests sont validés :

```bash
python -m pytest -v && python main.py
```

L’opérateur `&&` exécute le programme uniquement lorsque la commande de test se termine sans erreur.

---

## Organisation des tests

```text
tests/
├── unit/
│   ├── test_equipe.py
│   ├── test_participation.py
│   └── test_simulation_reponses.py
│
├── integration/
│   ├── test_connexion_service.py
│   ├── test_groupes_persistence.py
│   └── test_parcours_scolaire.py
│
├── contract/
│   ├── test_questionnaire_contract.py
│   ├── test_session_questionnaire_contract.py
│   └── test_statistiques_rapport_contract.py
│
└── functional/
    └── test_scenario_enseignant_qcm.py
```

---

## Organisation générale du projet

```text
quizzenClasse/
├── data/
│
├── database/
│   ├── models/
│   ├── services/
│   ├── base.py
│   ├── engine.py
│   └── tables_association.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── functional/
│
├── .gitignore
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

---

## Règles de contribution

Avant de commencer une modification :

```bash
git switch develop
```

Mettre à jour la branche locale :

```bash
git pull --ff-only origin develop
```

Créer une branche dédiée :

```bash
git switch -c feature/nom-fonctionnalite
```

Après le développement, exécuter les tests :

```bash
python -m pytest -v
```

Ajouter les fichiers concernés :

```bash
git add CHEMIN_DU_FICHIER
```

Créer un commit :

```bash
git commit -m "Description de la modification"
```

Envoyer la branche sur GitHub :

```bash
git push -u origin feature/nom-fonctionnalite
```

Une demande de fusion doit ensuite être créée sur GitHub vers la branche `develop`.

---

## Fichiers exclus du dépôt

Le fichier `.gitignore` exclut notamment :

* les environnements virtuels ;
* les caches Python ;
* les caches de pytest ;
* les bases SQLite locales ;
* les fichiers contenant des variables d’environnement ;
* les anciennes versions conservées dans `Old/` ;
* la documentation locale conservée dans `docs/`.

Les mots de passe, jetons d’accès et autres informations sensibles ne doivent jamais être ajoutés au dépôt.

---

## Auteurs

Projet réalisé dans le cadre de la Licence 2 Informatique.

Membres du groupe :

* Dominique ERIN;
* Fatima CHOKRI;
* Rokhaya-fall MEMMA.

Enseignant correcteur :

* Philippe KISLIN-DUVAL.

---

## Interface graphique, API et frontend web (nouvelle version)

En plus du programme console d'origine (python main.py), le projet propose
désormais une interface graphique de bureau (Tkinter), une API REST
(FastAPI) et un frontend web (React), qui communiquent tous les trois avec
la même base de données.

### Prérequis supplémentaires

* Node.js 18 ou plus récent, pour le frontend (nécessite glibc >= 2.28 sous
  Linux ; sur un système plus ancien, comme Ubuntu 18.04, préférer un test
  sous Windows/macOS ou dans un conteneur Docker).

### Configuration

Copier .env.example en .env à la racine du projet, et adapter si besoin
(seule la variable DATABASE_URL est obligatoire, les autres ont une
valeur par défaut) :

cp .env.example .env

### Installation

pip install -r requirements.txt

### Peupler la base des établissements scolaires (une seule fois)

python main.py seed-etabs

### Lancement (3 terminaux séparés)

Terminal 1 — l'API :

uvicorn api.app:app --reload

Terminal 2 — le frontend web (optionnel) :

cd frontend
npm install
npm run dev

Terminal 3 — l'interface graphique :

python gui_main.py

### Remarque pyenv

Si le fichier .python-version référence un environnement pyenv qui
n'existe pas sur votre machine (par exemple standalone-sqlalchemy), le
remplacer par votre propre version installée, par exemple :

echo "3.10.20" > .python-version
