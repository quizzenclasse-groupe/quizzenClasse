# database/engine.py
# *******************************************************
# Nom ......... : engine.py
# Rôle ........ : Charge la configuration de connexion depuis
#                 le fichier .env, crée le moteur SQLAlchemy
#                 et configure la fabrique de sessions utilisée
#                 pour accéder à la base de données.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile database/engine.py
# Usage ....... : Définir DATABASE_URL dans le fichier .env,
#                 puis importer :
#                 from database.engine import engine, Session
# *******************************************************
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Chemin racine du projet : ../ depuis database/
BASE_DIR = Path(__file__).resolve().parents[1]

# Chargement du fichier .env à la racine du projet
load_dotenv(BASE_DIR / ".env")

url = os.getenv("DATABASE_URL")

if not url:
    raise RuntimeError("DATABASE_URL manquante dans le fichier .env")

engine = create_engine(url)
# Implémentation de l’objet Session
Session = sessionmaker(engine)