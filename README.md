# QuizzenClasse

## Presentation

**QuizzenClasse** is an educational questionnaire management application developed as part of the second year of a Computer Science degree.

The project was developed in several versions using the same application core:

- a **command-line version**, developed by **Dominique ERIN**;
- a **graphical interface version**, developed by **Rokhaya-fall MEMMA**;
- a **version based on a REST API**, developed by **Fatima CHOKRI**, which can be used with the web frontend included in the project.

The application can notably:

- create and authenticate a teacher account;
- link a teacher to a school;
- manage school levels;
- create and assign students;
- create teams;
- create multiple-choice questionnaires;
- create and manage questionnaire sessions;
- evaluate participants;
- calculate statistics;
- generate session reports.

The core of the project mainly uses **Python**, **SQLAlchemy 2**, **SQLite** and **pytest**.

---

## Requirements

The project requires:

- Python 3.11 or a compatible version;
- Git;
- the Python dependencies listed in `requirements.txt`.

The project was developed with `pyenv` and `pyenv-virtualenv`, but using them is not mandatory.

Check the Python version:

```bash
python --version
```

Check the Git installation:

```bash
git --version
```

---

## Getting the project

Clone the GitHub repository:

```bash
git clone https://github.com/quizzenclasse-groupe/quizzenClasse.git
```

Move into the project directory:

```bash
cd quizzenClasse
```

---

## Activating the virtual environment

The virtual environment used during backend development was:

```text
standalone-sqlalchemy
```

It can be activated with:

```bash
pyenv activate standalone-sqlalchemy
```

Check the active environment:

```bash
pyenv version
```

The output should contain:

```text
standalone-sqlalchemy
```

Check the Python interpreter actually being used:

```bash
python -c "import sys; print(sys.executable)"
```

The path may look similar to:

```text
/home/USER/.pyenv/versions/standalone-sqlalchemy/bin/python
```

---

## Installing dependencies

Install the Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

Check the SQLAlchemy installation:

```bash
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Check the pytest installation:

```bash
python -m pytest --version
```

---

## Initializing the database

The application uses a SQLite database.

Missing tables are created automatically when the program starts.

The school data can be imported with:

```bash
python main.py seed-etabs
```

The default file used is:

```text
data/raw/education/fr-en-annuaire-education.csv
```

When the schools are already present in the database, the command may display:

```text
OK : 0 établissement(s) importé(s)
```

This result means that no new school was added.

---

## Running the tests

Before any important modification or any push to GitHub, run all the tests:

```bash
python -m pytest -v
```

The test suite includes:

- unit tests;
- integration tests;
- contract tests;
- the complete functional test.

### Run only the unit tests

```bash
python -m pytest tests/unit -v
```

### Run only the integration tests

```bash
python -m pytest tests/integration -v
```

### Run only the contract tests

```bash
python -m pytest tests/contract -v
```

### Run only the functional scenario

```bash
python -m pytest tests/functional -v
```

Changes should only be pushed to the remote repository after checking the test results.

---

# Running the different versions

QuizzenClasse can be used in several ways depending on the interface required.

## 1. Command-line version

The **command-line version was developed by Dominique ERIN**.

It gives direct access to the backend features from the terminal.

Run it with:

```bash
python main.py
```

The main menu includes:

```text
1. Se connecter
2. Créer un compte enseignant
3. Importer les établissements
4. Afficher les établissements
0. Quitter
```

After authentication, the teacher can access the features used to manage the school context, students, questionnaires, sessions, participations and reports.

To run all tests first and start the application only if they pass:

```bash
python -m pytest -v && python main.py
```

The `&&` operator starts the program only if the previous command finishes without an error.

---

## 2. Graphical interface version

The **graphical interface version was developed by Rokhaya-fall MEMMA**.

It allows users to access QuizzenClasse features through a graphical interface instead of directly from the terminal.

Run it with:

```bash
python gui_main.py
```

This interface uses the application core and the project data while providing graphical interaction for the user.

---

## 3. Version using the API

The **REST API was developed by Fatima CHOKRI**.

This version gives access to QuizzenClasse features through a FastAPI API. A web frontend is also included in the project and communicates with this API.

### Configuration

Copy the example file:

```bash
cp .env.example .env
```

Then change the environment variables when necessary.

### Installation

```bash
python -m pip install -r requirements.txt
```

### Populate the school database

This operation is only required once:

```bash
python main.py seed-etabs
```

### Run the API

In a first terminal:

```bash
uvicorn api.app:app --reload
```

### Run the web frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend uses the FastAPI API to communicate with the backend features.

Node.js 18 or a more recent version is required for this part of the project.

---

## Contribution rules

Before starting a modification:

```bash
git switch develop
```

Update the local branch:

```bash
git pull --ff-only origin develop
```

Create a dedicated branch:

```bash
git switch -c feature/feature-name
```

After development, run the tests:

```bash
python -m pytest -v
```

Add the related files:

```bash
git add FILE_PATH
```

Create a commit:

```bash
git commit -m "Description of the change"
```

Push the branch to GitHub:

```bash
git push -u origin feature/feature-name
```

A merge request can then be created toward the `develop` branch.

---

## Files excluded from the repository

The `.gitignore` file excludes notably:

- virtual environments;
- Python caches;
- pytest caches;
- local SQLite databases;
- files containing environment variables;
- local frontend dependencies such as `node_modules/`;
- old versions stored in `Old/`;
- local documentation stored in `docs/`.

Passwords, access tokens and other sensitive information must never be added to the repository.

---

## Authors and contributions

Project developed as part of the **second year of a Computer Science degree**.

### Dominique ERIN

- design and development of the Python backend;
- business model design;
- persistence with SQLAlchemy;
- command-line version;
- backend tests.

### Fatima CHOKRI

- development of the REST API.

### Rokhaya-fall MEMMA

- development of the graphical interface.

### Supervising teacher

- Philippe KISLIN-DUVAL.

## License

The source code authored by Dominique ERIN is made available for personal
evaluation, educational review, and recruitment purposes only.

Redistribution, derivative works, and commercial use are not permitted
without prior written permission.

## See the [LICENSE](LICENSE) file for details.

## Note about pyenv

If the `.python-version` file refers to a `pyenv` environment that does not exist on the current computer, it can be replaced by a compatible Python version installed locally.

Example:

```bash
echo "3.11" > .python-version
```
