"""Point d'entrée de l'application : création de l'API FastAPI, CORS et routeurs."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import charger_livres_de_depart, creer_tables, engine
from app.routers import livres

# Seule l'origine du frontend (Live Server) est autorisée : pas d'astérisque.
# Une origine = protocole + adresse + port, sans le chemin (pas de /index.html).
ORIGINES_AUTORISEES = ["http://127.0.0.1:5500"]


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

# CORS : le navigateur n'autorise la page du frontend à parler à l'API
# que si l'API le permet explicitement
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_AUTORISEES,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Branche les points d'accès de livres.py sur l'application
app.include_router(livres.router)


@app.get(
    "/sante",
    tags=["Santé"],
    summary="Vérifier que l'API fonctionne",
    description="Renvoie toujours `{\"statut\": \"ok\"}` quand le serveur répond.",
)
def sante():
    return {"statut": "ok"}
