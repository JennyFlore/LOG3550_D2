"""Point d'entrée de l'application : création de l'API FastAPI.

Les routeurs (Partie 3) et le CORS (Partie 6) seront ajoutés dans les
prochaines étapes.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from app.database import charger_livres_de_depart, creer_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Code exécuté une fois au démarrage du serveur, avant la première requête."""
    creer_tables()
    with Session(engine) as session:
        charger_livres_de_depart(session)
    yield


app = FastAPI(
    title="API Catalogue de bibliothèque",
    description="API REST pour gérer les livres d'une bibliothèque (LOG3550, Devoir 2).",
    version="1.0.0",
    lifespan=lifespan,
)
