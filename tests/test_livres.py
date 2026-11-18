"""Tests automatiques de l'API avec pytest et TestClient.

Chaque test utilise sa propre base SQLite EN MÉMOIRE (séparée de bibliotheque.db),
déjà remplie avec les 10 livres de départ.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import charger_livres_de_depart, get_session
from app.main import app

NOUVEAU_LIVRE = {
    "titre": "Dune",
    "auteur": "Frank Herbert",
    "annee": 1965,
    "categorie": "roman",
}


@pytest.fixture
def client():
    """Client de test branché sur une base en mémoire, neuve pour chaque test."""
    moteur = create_engine(
        "sqlite://",  # base en mémoire
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # garde la même connexion, sinon la base mémoire disparaît
    )
    SQLModel.metadata.create_all(moteur)
    with Session(moteur) as session:
        charger_livres_de_depart(session)

    def session_de_test():
        with Session(moteur) as session:
            yield session

    # Remplace la vraie base par la base de test, pour toute l'application
    app.dependency_overrides[get_session] = session_de_test
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------- Création ----------

def test_creer_livre(client):
    reponse = client.post("/livres", json=NOUVEAU_LIVRE)

    assert reponse.status_code == 201
    livre = reponse.json()
    assert livre["id"] == 11  # les 10 livres de départ ont les id 1 à 10
    assert livre["titre"] == "Dune"
    assert livre["disponible"] is True  # valeur par défaut
    assert reponse.headers["location"].endswith("/livres/11")


# ---------- Lecture ----------

def test_lire_livre(client):
    reponse = client.get("/livres/1")

    assert reponse.status_code == 200
    assert reponse.json()["titre"] == "Le Petit Prince"


def test_lister_livres_de_depart(client):
    reponse = client.get("/livres")

    assert reponse.status_code == 200
    assert len(reponse.json()) == 10


def test_liste_filtree(client):
    reponse = client.get("/livres", params={"categorie": "roman", "disponible": True})

    titres = [livre["titre"] for livre in reponse.json()]
    assert titres == ["Le Petit Prince", "Gouverneurs de la rosée"]


def test_recherche_par_titre_ou_auteur(client):
    par_titre = client.get("/livres", params={"q": "cosmos"}).json()
    par_auteur = client.get("/livres", params={"q": "CAMUS"}).json()  # sans tenir compte de la casse

    assert [livre["titre"] for livre in par_titre] == ["Cosmos"]
    assert [livre["titre"] for livre in par_auteur] == ["L'Étranger"]


def test_pagination(client):
    reponse = client.get("/livres", params={"skip": 2, "limit": 3})

    assert [livre["id"] for livre in reponse.json()] == [3, 4, 5]


# ---------- Mise à jour ----------

def test_remplacer_livre_avec_put(client):
    remplacement = {**NOUVEAU_LIVRE, "isbn": "1234567890"}
    assert client.put("/livres/1", json=remplacement).status_code == 200

    # PUT remplace tout : sans ISBN dans la demande, l'ISBN est effacé
    reponse = client.put("/livres/1", json=NOUVEAU_LIVRE)

    assert reponse.status_code == 200
    assert reponse.json()["titre"] == "Dune"
    assert reponse.json()["isbn"] is None


def test_modifier_livre_avec_patch(client):
    avant = client.get("/livres/1").json()

    reponse = client.patch("/livres/1", json={"disponible": False})

    apres = reponse.json()
    assert reponse.status_code == 200
    assert apres["disponible"] is False
    assert apres["titre"] == avant["titre"]  # les autres champs ne bougent pas


# ---------- Suppression ----------

def test_supprimer_livre(client):
    reponse = client.delete("/livres/1")

    assert reponse.status_code == 204
    assert client.get("/livres/1").status_code == 404


# ---------- Erreurs 404, 422 et 409 ----------

@pytest.mark.parametrize(
    "methode, chemin, corps",
    [
        ("get", "/livres/999", None),
        ("put", "/livres/999", NOUVEAU_LIVRE),
        ("patch", "/livres/999", {"disponible": False}),
        ("delete", "/livres/999", None),
    ],
)
def test_livre_inexistant_renvoie_404(client, methode, chemin, corps):
    reponse = client.request(methode, chemin, json=corps)

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Livre introuvable"}


@pytest.mark.parametrize(
    "changement",
    [
        {"titre": "A"},                # titre trop court
        {"auteur": "B" * 201},         # auteur trop long
        {"annee": 1449},               # année avant 1450
        {"annee": 9999},               # année dans le futur
        {"categorie": "cuisine"},      # catégorie hors de la liste
        {"isbn": "12345"},             # ISBN ni de 10 ni de 13 chiffres
        {"id": 50},                    # identifiant fourni par le client
    ],
)
def test_donnees_invalides_renvoient_422(client, changement):
    reponse = client.post("/livres", json={**NOUVEAU_LIVRE, **changement})

    assert reponse.status_code == 422
    assert "detail" in reponse.json()


def test_isbn_en_double_renvoie_409(client):
    avec_isbn = {**NOUVEAU_LIVRE, "isbn": "1234567890"}
    assert client.post("/livres", json=avec_isbn).status_code == 201

    reponse = client.post("/livres", json={**avec_isbn, "titre": "Autre livre"})

    assert reponse.status_code == 409
    assert reponse.json() == {"detail": "Un livre avec cet ISBN existe déjà"}


# ---------- Santé ----------

def test_sante(client):
    reponse = client.get("/sante")

    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}
