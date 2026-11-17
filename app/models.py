"""Modèle de la table Livre, stockée dans la base de données SQLite."""
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Categorie(str, Enum):
    """Catégories autorisées. Toute autre valeur est refusée (erreur 422)."""

    roman = "roman"
    science = "science"
    histoire = "histoire"
    informatique = "informatique"
    autre = "autre"


class Livre(SQLModel, table=True):
    """Une ligne de la table « livre ». table=True : SQLModel crée la table."""

    id: Optional[int] = Field(default=None, primary_key=True)  # généré par la base
    titre: str
    auteur: str
    annee: int
    categorie: Categorie
    # unique + index : la BASE refuse deux livres avec le même ISBN.
    # Plusieurs livres sans ISBN (NULL) restent permis.
    isbn: Optional[str] = Field(default=None, unique=True, index=True)
    disponible: bool = True
