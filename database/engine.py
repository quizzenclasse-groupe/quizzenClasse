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