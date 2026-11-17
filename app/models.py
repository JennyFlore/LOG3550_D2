"""Modèle de la table Livre, stockée dans la base de données.

La table elle-même sera ajoutée à la Partie 4. Pour l'instant, ce fichier
contient seulement la liste des catégories autorisées.
"""
from enum import Enum


class Categorie(str, Enum):
    """Catégories autorisées. Toute autre valeur est refusée (erreur 422)."""

    roman = "roman"
    science = "science"
    histoire = "histoire"
    informatique = "informatique"
    autre = "autre"
