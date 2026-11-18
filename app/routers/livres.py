"""Points d'accès (endpoints) de l'API pour les livres."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, or_, select

from app.database import get_session
from app.models import Categorie, Livre
from app.schemas import LivreCreate, LivreRead, LivreUpdate

# Tous les chemins de ce fichier commencent par /livres
router = APIRouter(prefix="/livres", tags=["Livres"])


# ---------- Fonctions utilitaires (évitent de répéter le même code) ----------

def trouver_livre(session: Session, id: int) -> Livre:
    """Renvoie le livre demandé, ou répond 404 s'il n'existe pas."""
    livre = session.get(Livre, id)
    if livre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable")
    return livre


def enregistrer(session: Session, livre: Livre) -> Livre:
    """Enregistre le livre. Si la base refuse l'ISBN (doublon), répond 409."""
    session.add(livre)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()  # annule la tentative pour garder la session utilisable
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un livre avec cet ISBN existe déjà",
        )
    session.refresh(livre)  # recharge le livre avec les valeurs de la base (dont l'id)
    return livre


# ---------- Lire ----------

@router.get(
    "",
    response_model=list[LivreRead],
    summary="Lister les livres",
    description="Renvoie les livres, triés par id. Tous les filtres sont facultatifs "
    "et peuvent être combinés. La pagination se fait avec `skip` et `limit` (100 au maximum).",
)
def lister_livres(
    q: Optional[str] = Query(None, description="Texte cherché dans le titre ou l'auteur"),
    categorie: Optional[Categorie] = Query(None, description="Garder une seule catégorie"),
    disponible: Optional[bool] = Query(None, description="true : disponibles, false : empruntés"),
    skip: int = Query(0, ge=0, description="Nombre de livres à sauter"),
    limit: int = Query(100, ge=1, le=100, description="Nombre maximal de livres renvoyés"),
    session: Session = Depends(get_session),
):
    requete = select(Livre)
    if q and q.strip():
        texte = q.strip()
        requete = requete.where(
            or_(
                Livre.titre.icontains(texte, autoescape=True),
                Livre.auteur.icontains(texte, autoescape=True),
            )
        )
    if categorie is not None:
        requete = requete.where(Livre.categorie == categorie)
    if disponible is not None:
        requete = requete.where(Livre.disponible == disponible)

    return session.exec(requete.order_by(Livre.id).offset(skip).limit(limit)).all()


@router.get(
    "/{id}",
    response_model=LivreRead,
    summary="Lire un livre",
    description="Renvoie le livre dont l'id est donné, ou une erreur 404 s'il n'existe pas.",
    responses={404: {"description": "Livre introuvable"}},
)
def lire_livre(id: int, session: Session = Depends(get_session)):
    return trouver_livre(session, id)


# ---------- Créer ----------

@router.post(
    "",
    response_model=LivreRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un livre",
    description="Crée un livre. L'id est généré par la base. La réponse porte l'en-tête "
    "`Location` qui donne l'adresse du nouveau livre.",
    responses={409: {"description": "Un livre avec cet ISBN existe déjà"}},
)
def creer_livre(
    donnees: LivreCreate,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
):
    livre = enregistrer(session, Livre(**donnees.model_dump()))
    response.headers["Location"] = str(request.url_for("lire_livre", id=livre.id))
    return livre


# ---------- Modifier ----------

@router.put(
    "/{id}",
    response_model=LivreRead,
    summary="Remplacer un livre",
    description="Remplacement complet : tous les champs obligatoires doivent être envoyés. "
    "Un champ facultatif absent (comme `isbn`) est effacé.",
    responses={404: {"description": "Livre introuvable"}, 409: {"description": "ISBN déjà utilisé"}},
)
def remplacer_livre(id: int, donnees: LivreCreate, session: Session = Depends(get_session)):
    livre = trouver_livre(session, id)
    for champ, valeur in donnees.model_dump().items():
        setattr(livre, champ, valeur)
    return enregistrer(session, livre)


@router.patch(
    "/{id}",
    response_model=LivreRead,
    summary="Modifier un livre en partie",
    description="Modification partielle : seuls les champs envoyés sont changés, "
    "les autres restent tels quels.",
    responses={404: {"description": "Livre introuvable"}, 409: {"description": "ISBN déjà utilisé"}},
)
def modifier_livre(id: int, donnees: LivreUpdate, session: Session = Depends(get_session)):
    livre = trouver_livre(session, id)
    # exclude_unset : on ne garde que les champs réellement envoyés par le client
    for champ, valeur in donnees.model_dump(exclude_unset=True).items():
        setattr(livre, champ, valeur)
    return enregistrer(session, livre)


# ---------- Supprimer ----------

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un livre",
    description="Supprime le livre. La réponse 204 ne contient pas de corps.",
    responses={404: {"description": "Livre introuvable"}},
)
def supprimer_livre(id: int, session: Session = Depends(get_session)):
    livre = trouver_livre(session, id)
    session.delete(livre)
    session.commit()
