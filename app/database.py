"""Moteur SQLite, session de base de données et livres de départ."""
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import Categorie, Livre

# Le fichier bibliotheque.db est créé à côté de l'application (ignoré par Git)
DATABASE_URL = "sqlite:///./bibliotheque.db"

# check_same_thread=False : SQLite accepte d'être utilisé par plusieurs fils d'exécution
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Données brutes (dictionnaires) : chaque démarrage crée de nouveaux objets Livre
LIVRES_DE_DEPART = [
    {"titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupéry", "annee": 1943, "categorie": Categorie.roman},
    {"titre": "Gouverneurs de la rosée", "auteur": "Jacques Roumain", "annee": 1944, "categorie": Categorie.roman},
    {"titre": "L'Étranger", "auteur": "Albert Camus", "annee": 1942, "categorie": Categorie.roman, "disponible": False},
    {"titre": "Une brève histoire du temps", "auteur": "Stephen Hawking", "annee": 1988, "categorie": Categorie.science, "disponible": False},
    {"titre": "Cosmos", "auteur": "Carl Sagan", "annee": 1980, "categorie": Categorie.science},
    {"titre": "Sapiens", "auteur": "Yuval Noah Harari", "annee": 2011, "categorie": Categorie.histoire},
    {"titre": "Les Jacobins noirs", "auteur": "C. L. R. James", "annee": 1938, "categorie": Categorie.histoire, "disponible": False},
    {"titre": "Clean Code", "auteur": "Robert C. Martin", "annee": 2008, "categorie": Categorie.informatique},
    {"titre": "Eloquent JavaScript", "auteur": "Marijn Haverbeke", "annee": 2011, "categorie": Categorie.informatique},
    {"titre": "Éloge de la créolité", "auteur": "Bernabé, Chamoiseau, Confiant", "annee": 1989, "categorie": Categorie.autre},
]


def creer_tables() -> None:
    """Crée les tables qui n'existent pas encore (appelée au démarrage)."""
    SQLModel.metadata.create_all(engine)


def charger_livres_de_depart(session: Session) -> None:
    """Ajoute les livres de départ, seulement si la table est vide."""
    if session.exec(select(Livre).limit(1)).first() is None:
        session.add_all([Livre(**donnees) for donnees in LIVRES_DE_DEPART])
        session.commit()


def get_session():
    """Dépendance FastAPI : une session par requête, fermée après la requête."""
    with Session(engine) as session:
        yield session
