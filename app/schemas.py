"""Schémas Pydantic : ce que le client envoie (LivreCreate, LivreUpdate)
et ce que l'API renvoie (LivreRead). Ils portent les règles de validation.
"""
from datetime import date
from typing import Annotated, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from app.models import Categorie

ANNEE_MIN = 1450

# ---------- Types réutilisables : chaque règle n'est écrite qu'une fois ----------

# Texte de 2 à 200 caractères, espaces au début et à la fin retirés
Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=200)]

# ISBN : exactement 10 ou 13 chiffres
Isbn = Annotated[str, StringConstraints(pattern=r"^(\d{10}|\d{13})$")]


def verifier_annee_pas_future(annee: int) -> int:
    """Refuse une année après l'année en cours (calculée à chaque appel)."""
    annee_courante = date.today().year
    if annee > annee_courante:
        raise ValueError(f"L'année ne peut pas dépasser {annee_courante}")
    return annee


# Année entre 1450 (ge = greater or equal) et l'année en cours
Annee = Annotated[int, Field(ge=ANNEE_MIN), AfterValidator(verifier_annee_pas_future)]


# ---------- Schémas ----------

class LivreCreate(BaseModel):
    """Corps d'une demande POST /livres. Aucun id : il est généré par la base."""

    # forbid : un champ inconnu (par exemple "id") est refusé avec une erreur 422
    # json_schema_extra : l'exemple affiché dans /docs (Swagger)
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "titre": "Le Petit Prince",
                    "auteur": "Antoine de Saint-Exupéry",
                    "annee": 1943,
                    "categorie": "roman",
                    "isbn": "9782070612758",
                    "disponible": True,
                }
            ]
        },
    )

    titre: Texte
    auteur: Texte
    annee: Annee
    categorie: Categorie
    isbn: Optional[Isbn] = None
    disponible: bool = True


class LivreUpdate(BaseModel):
    """Corps d'une demande PUT (remplacement) ou PATCH (modification partielle).

    Tous les champs sont facultatifs : on n'envoie que ceux à modifier.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"disponible": False}]},
    )

    titre: Optional[Texte] = None
    auteur: Optional[Texte] = None
    annee: Optional[Annee] = None
    categorie: Optional[Categorie] = None
    isbn: Optional[Isbn] = None
    disponible: Optional[bool] = None

    @model_validator(mode="after")
    def refuser_valeur_nulle(self):
        """Un champ obligatoire peut être absent, mais pas envoyé avec null."""
        for nom in ("titre", "auteur", "annee", "categorie", "disponible"):
            if nom in self.model_fields_set and getattr(self, nom) is None:
                raise ValueError(f"Le champ '{nom}' ne peut pas être null")
        return self


class LivreRead(BaseModel):
    """Réponse de l'API : un livre complet, avec son id généré."""

    # from_attributes : permet de construire ce schéma à partir d'un objet de la base
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "titre": "Le Petit Prince",
                    "auteur": "Antoine de Saint-Exupéry",
                    "annee": 1943,
                    "categorie": "roman",
                    "isbn": "9782070612758",
                    "disponible": True,
                }
            ]
        },
    )

    id: int
    titre: str
    auteur: str
    annee: int
    categorie: Categorie
    isbn: Optional[str] = None
    disponible: bool
