#database/base.py
# *******************************************************
# Nom ......... : base.py
# Rôle ........ : Définit la classe de base déclarative commune
#                 à tous les modèles ORM SQLAlchemy ainsi que
#                 la convention de nommage des index, clés et
#                 contraintes de la base de données.
# Auteur ...... : Dominique ERIN
# Version ..... : V0.1 du 30/07/2026
# Licence ..... : réalisé dans le cadre du cours de
#                 Réalisation de programme
#                 (2025/2026)
# Compilation . : python -m py_compile database/base.py
# Usage ....... : Importer la classe de base avec :
#                 from database.base import Model
# *******************************************************
from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

class Model(DeclarativeBase):
		metadata = MetaData(naming_convention={
		"ix": "ix_%(column_0_label)s",
		"uq": "uq_%(table_name)s_%(column_0_name)s",
		"ck": "ck_%(table_name)s_%(constraint_name)s",
		"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
		"pk": "pk_%(table_name)s",
	})