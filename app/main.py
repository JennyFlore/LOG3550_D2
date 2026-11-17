"""Point d'entrée de l'application : création de l'API FastAPI.

Les routeurs (Partie 3), la base de données (Partie 4) et le CORS (Partie 6)
seront ajoutés dans les prochaines étapes.
"""
from fastapi import FastAPI

app = FastAPI(
    title="API Catalogue de bibliothèque",
    description="API REST pour gérer les livres d'une bibliothèque (LOG3550, Devoir 2).",
    version="1.0.0",
)
