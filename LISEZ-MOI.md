# QuizzenClasse

## Présentation

**QuizzenClasse** est une application de gestion de questionnaires pédagogiques réalisée dans le cadre de la Licence 3 Informatique.

Le projet a été développé en plusieurs versions permettant d'exploiter le même cœur applicatif :

- une **version en ligne de commande**, réalisée par **Dominique ERIN** ;
- une **version avec interface graphique**, réalisée par **Rokhaya-fall MEMMA** ;
- une **version reposant sur une API REST**, développée par **Fatima CHOKRI**, et pouvant être utilisée avec le frontend web présent dans le projet.

L’application permet notamment :

- la création et l’authentification d’un compte enseignant ;
- le rattachement d’un enseignant à un établissement ;
- la gestion des niveaux scolaires ;
- la création et l’affectation des élèves ;
- la constitution d’équipes ;
- la création de questionnaires à choix multiples ;
- la création et le suivi de sessions de questionnaire ;
- l’évaluation des participants ;
- le calcul des statistiques ;
- la génération de rapports de session.

Le cœur du projet utilise notamment **Python**, **SQLAlchemy 2**, **SQLite** et **pytest**.

---

## Prérequis

Le projet nécessite :

- Python 3.11 ou une version compatible ;
- Git ;
- les dépendances Python présentes dans `requirements.txt`.

Le projet a été développé avec `pyenv` et `pyenv-virtualenv`, mais leur utilisation n'est pas obligatoire.

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
git clone https://github.com/quizzenclasse-groupe/quizzenClasse.git
```

Se placer dans le répertoire du projet :

```bash
cd quizzenClasse
```

---

## Activation de l’environnement virtuel

L’environnement virtuel utilisé pendant le développement du backend était :

```text
standalone-sqlalchemy
```

Il peut être activé avec :

```bash
pyenv activate standalone-sqlalchemy
```

Vérifier l’environnement utilisé :

```bash
pyenv version
```

La sortie doit alors contenir :

```text
standalone-sqlalchemy
```

Vérifier l’interpréteur Python réellement utilisé :

```bash
python -c "import sys; print(sys.executable)"
```

Le chemin obtenu peut être similaire à :

```text
/home/UTILISATEUR/.pyenv/versions/standalone-sqlalchemy/bin/python
```

---

## Installation des dépendances

Installer les dépendances Python avec :

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

- les tests unitaires ;
- les tests d’intégration ;
- les tests de contrat ;
- le test fonctionnel complet.

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

# Lancement des différentes versions

QuizzenClasse peut être utilisé de plusieurs manières selon l'interface souhaitée.

## 1. Version en ligne de commande

La **version en ligne de commande a été réalisée par Dominique ERIN**.

Elle permet d'accéder directement aux fonctionnalités du backend à partir du terminal.

Elle se lance avec :

```bash
python main.py
```

Le menu principal permet notamment :

```text
1. Se connecter
2. Créer un compte enseignant
3. Importer les établissements
4. Afficher les établissements
0. Quitter
```

Après authentification, l’enseignant accède aux fonctions de gestion du parcours scolaire, des élèves, des questionnaires, des sessions, des participations et des rapports.

Pour exécuter préalablement l’ensemble des tests puis lancer l’application uniquement lorsque ceux-ci réussissent :

```bash
python -m pytest -v && python main.py
```

L’opérateur `&&` lance le programme uniquement lorsque la commande précédente se termine sans erreur.

---

## 2. Version avec interface graphique

La **version avec interface graphique a été réalisée par Rokhaya-fall MEMMA**.

Elle permet d'utiliser les fonctionnalités de QuizzenClasse à partir d'une interface graphique plutôt que directement depuis le terminal.

Elle se lance avec :

```bash
python gui_main.py
```

Cette interface exploite le cœur applicatif et les données du projet tout en proposant une interaction graphique avec l'utilisateur.

---

## 3. Version utilisant l’API

L’**API REST a été développée par Fatima CHOKRI**.

Cette version permet d'accéder aux fonctionnalités de QuizzenClasse à travers une API FastAPI. Un frontend web est également présent dans le projet et communique avec cette API.

### Configuration

Copier le fichier d’exemple :

```bash
cp .env.example .env
```

Puis adapter les variables d’environnement lorsque cela est nécessaire.

### Installation

```bash
python -m pip install -r requirements.txt
```

### Peupler la base des établissements scolaires

Cette opération n'est nécessaire qu'une seule fois :

```bash
python main.py seed-etabs
```

### Lancement de l’API

Dans un premier terminal :

```bash
uvicorn api.app:app --reload
```

### Lancement du frontend web

Dans un second terminal :

```bash
cd frontend
npm install
npm run dev
```

Le frontend utilise donc l’API FastAPI pour communiquer avec les fonctionnalités du backend.

Node.js 18 ou une version plus récente est nécessaire pour cette partie du projet.

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

Une demande de fusion peut ensuite être créée vers la branche `develop`.

---

## Fichiers exclus du dépôt

Le fichier `.gitignore` exclut notamment :

- les environnements virtuels ;
- les caches Python ;
- les caches de pytest ;
- les bases SQLite locales ;
- les fichiers contenant des variables d’environnement ;
- les dépendances locales du frontend telles que `node_modules/` ;
- les anciennes versions conservées dans `Old/` ;
- la documentation locale conservée dans `docs/`.

Les mots de passe, jetons d’accès et autres informations sensibles ne doivent jamais être ajoutés au dépôt.

---

## Auteurs et contributions

Projet réalisé dans le cadre de la **Licence 2 Informatique**.

### Dominique ERIN

- conception et développement du backend Python ;
- modélisation métier ;
- persistance avec SQLAlchemy ;
- version en ligne de commande ;
- tests du backend.

### Fatima CHOKRI

- développement de l’API REST.

### Rokhaya-fall MEMMA

- développement de l’interface graphique.

### Enseignant correcteur

- Philippe KISLIN-DUVAL.

## License

Le code source créé par Dominique ERIN est mis à disposition à des fins personnelles
d'évaluation, de révision pédagogique et de recrutement uniquement.

Toute redistribution, création d'œuvres dérivées et utilisation commerciale est interdite
sans autorisation écrite préalable.

## Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## Remarque sur pyenv

Si le fichier `.python-version` référence un environnement `pyenv` qui n'existe pas sur la machine utilisée, il peut être remplacé par une version de Python compatible installée localement.

Exemple :

```bash
echo "3.11" > .python-version
```
