# API Catalogue de bibliothèque — LOG3550 Devoir 2

**Étudiante :** Jenny Flore CHERFILS

**Cours :** LOG3550 Développement web, ISTEAH, professeur Samuel Jonathan Joseph

**Dépôt Git :** https://github.com/JennyFlore/LOG3550_D2

Projet en cours de réalisation. Les sections « Installation », « Lancement », « Tests » et « Sources » seront complétées à la fin.

## Réponses aux questions d'explication

### Partie 1 : rôle de FastAPI, d'Uvicorn et de Pydantic, et séparation modèle / schémas

FastAPI est l'outil Python qui sert à construire l'API : il reçoit les demandes, appelle notre code et crée la page de documentation `/docs`. Uvicorn est le serveur qui fait marcher l'application et qui reçoit les demandes venant du réseau ; sans lui, FastAPI ne peut pas répondre. Pydantic vérifie les données, par exemple qu'une année est bien un nombre et qu'un titre n'est pas trop court. On sépare le modèle de base de données, qui décrit la table, des schémas d'échange, qui décrivent ce que le client envoie et reçoit, parce que ce n'est pas la même chose : le client ne doit pas choisir l'`id`, et la table peut contenir des champs que le client ne doit pas voir. Ainsi, on peut changer l'un sans casser l'autre.
