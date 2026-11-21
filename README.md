# API Catalogue de bibliothèque — LOG3550 Devoir 2

**Étudiante :** Jenny Flore CHERFILS

**Cours :** LOG3550 Développement web ||, ISTEAH, professeur Samuel Jonathan Joseph

**Dépôt Git :** https://github.com/JennyFlore/LOG3550_D2

## Description

API REST construite avec FastAPI pour gérer le catalogue d'une bibliothèque : lire, créer, remplacer, modifier et supprimer des livres. Les données sont validées avec Pydantic et enregistrées dans une base SQLite avec SQLModel. Au premier démarrage, 10 livres de départ sont chargés si la table est vide. L'API reste en local (aucune clé ni mot de passe).

Un livre a : `id` (généré), `titre`, `auteur`, `annee`, `categorie` (roman, science, histoire, informatique ou autre), `isbn` (facultatif, unique) et `disponible` (vrai par défaut).

## Installation

Il faut Python 3.10 ou plus et Git. Dans un terminal, depuis le dossier `devoir2` (exemple pour Windows PowerShell) :

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
pip install -r requirements.txt
```

Si le fichier `requirements.txt` est absent, installer à la main : `pip install fastapi "uvicorn[standard]" sqlmodel pytest httpx`.

## Lancement

Avec l'environnement virtuel activé (`(.venv)` visible au début de la ligne) :

```powershell
uvicorn app.main:app --reload
```

L'API répond sur `http://127.0.0.1:8000` et la documentation interactive (Swagger) est sur `http://127.0.0.1:8000/docs`. Le fichier `bibliotheque.db` est créé automatiquement au premier démarrage. Pour arrêter le serveur : `Ctrl + C`.

## Tests

```powershell
pytest -v
```

Les tests utilisent une base SQLite en mémoire, séparée de `bibliotheque.db`, et se lancent sans démarrer le serveur.

## Points d'accès

| Méthode | Chemin | Rôle | Réponses |
|---|---|---|---|
| GET | `/livres` | Liste, filtres `q`, `categorie`, `disponible`, pagination `skip` et `limit` (100 au maximum) | 200, 422 |
| GET | `/livres/{id}` | Lire un livre | 200, 404 |
| POST | `/livres` | Créer un livre | 201 (avec l'en-tête `Location`), 409, 422 |
| PUT | `/livres/{id}` | Remplacer un livre au complet | 200, 404, 409, 422 |
| PATCH | `/livres/{id}` | Modifier un livre en partie | 200, 404, 409, 422 |
| DELETE | `/livres/{id}` | Supprimer un livre | 204, 404 |
| GET | `/sante` | Vérifier que l'API répond | 200 `{"statut": "ok"}` |

Chaque erreur renvoie du JSON avec un message clair (par exemple `{"detail": "Livre introuvable"}`).

## Frontend (Partie 6)

Le frontend du devoir 1 est dans le dossier `frontend/`. Il lit, ajoute, emprunte et supprime les livres par l'API avec `fetch` (`async` et `await`), et n'utilise plus `localStorage`. Il affiche « Chargement des livres… » pendant que l'API répond, et un message d'erreur avec un bouton « Réessayer » si l'API est arrêtée. Le bouton « Réinitialiser » et le fichier `data.js` ont été retirés : les livres de départ sont maintenant chargés par l'API dans la base de données.

Pour l'utiliser, il faut démarrer **deux choses** :

1. L'API, dans un terminal (voir « Lancement ») : `uvicorn app.main:app --reload`.
2. Le frontend, avec l'extension Live Server de VS Code : clic droit sur `frontend/index.html` puis « Open with Live Server ».

La page doit s'ouvrir à l'adresse **`http://127.0.0.1:5500`**. Le CORS de l'API autorise uniquement cette origine (pas d'astérisque) : avec `http://localhost:5500`, le navigateur bloque les demandes et la page affiche « Impossible de joindre l'API ».

## Réponses aux questions d'explication

### Partie 1 : rôle de FastAPI, d'Uvicorn et de Pydantic, et séparation modèle / schémas

FastAPI est l'outil Python qui sert à construire l'API : il reçoit les demandes, appelle notre code et crée la page de documentation `/docs`. Uvicorn est le serveur qui fait marcher l'application et qui reçoit les demandes venant du réseau ; sans lui, FastAPI ne peut pas répondre. Pydantic vérifie les données, par exemple qu'une année est bien un nombre et qu'un titre n'est pas trop court. On sépare le modèle de base de données, qui décrit la table, des schémas d'échange, qui décrivent ce que le client envoie et reçoit, parce que ce n'est pas la même chose : le client ne doit pas choisir l'`id`, et la table peut contenir des champs que le client ne doit pas voir. Ainsi, on peut changer l'un sans casser l'autre.

### Partie 2 : format de l'erreur 422

Quand les données envoyées ne respectent pas les règles, l'API répond avec le code 422 et un JSON qui contient une liste `detail`. Chaque élément de la liste décrit une erreur : `loc` indique où est le problème (par exemple `body` puis le nom du champ, comme `titre`), `msg` explique le problème, `type` donne le genre d'erreur (par exemple `string_too_short`), `input` montre la valeur reçue et `ctx` rappelle la règle (par exemple `min_length: 2`). S'il y a plusieurs erreurs, elles apparaissent toutes dans la même réponse.

### Partie 3 : différence entre PUT et PATCH, et idempotence

PUT remplace le livre au complet : il faut envoyer tous les champs obligatoires, et un champ facultatif qu'on n'envoie pas (comme l'ISBN) est effacé. PATCH ne change que les champs envoyés et laisse les autres intacts. PUT est idempotent : envoyer la même demande une fois ou dix fois donne le même résultat final. DELETE l'est aussi : après la première suppression le livre n'existe plus, et les demandes suivantes ne changent plus rien (seule la réponse change, 404 au lieu de 204). POST n'est pas idempotent : chaque demande crée un nouveau livre avec un nouvel `id`, donc répéter la demande crée des doublons.

## Sources et outils d'assistance utilisés

- Assistant IA : Claude (Anthropic), utilisé pour m'aider à réaliser ce devoir étape par étape : explication des termes, proposition de code et de tests, relecture. J'ai exécuté et lu le code avant de le garder.
- Documentation officielle de FastAPI (https://fastapi.tiangolo.com), de SQLModel (https://sqlmodel.tiangolo.com), de Pydantic (https://docs.pydantic.dev) et de pytest (https://docs.pytest.org).
- Outils : Visual Studio Code, Git et GitHub, Python et pip.
