# API Catalogue de bibliothèque — LOG3550 Devoir 2

**Étudiante :** Jenny Flore CHERFILS

**Cours :** LOG3550 Développement web ||, ISTEAH, professeur Samuel Jonathan Joseph

**Dépôt Git :** https://github.com/JennyFlore/LOG3550_D2

Projet en cours de réalisation. Les sections « Installation », « Lancement », « Tests » et « Sources » seront complétées à la fin.

## Réponses aux questions d'explication

### Partie 1 : rôle de FastAPI, d'Uvicorn et de Pydantic, et séparation modèle / schémas

FastAPI est l'outil Python qui sert à construire l'API : il reçoit les demandes, appelle notre code et crée la page de documentation `/docs`. Uvicorn est le serveur qui fait marcher l'application et qui reçoit les demandes venant du réseau ; sans lui, FastAPI ne peut pas répondre. Pydantic vérifie les données, par exemple qu'une année est bien un nombre et qu'un titre n'est pas trop court. On sépare le modèle de base de données, qui décrit la table, des schémas d'échange, qui décrivent ce que le client envoie et reçoit, parce que ce n'est pas la même chose : le client ne doit pas choisir l'`id`, et la table peut contenir des champs que le client ne doit pas voir. Ainsi, on peut changer l'un sans casser l'autre.

### Partie 2 : format de l'erreur 422

Quand les données envoyées ne respectent pas les règles, l'API répond avec le code 422 et un JSON qui contient une liste `detail`. Chaque élément de la liste décrit une erreur : `loc` indique où est le problème (par exemple `body` puis le nom du champ, comme `titre`), `msg` explique le problème, `type` donne le genre d'erreur (par exemple `string_too_short`), `input` montre la valeur reçue et `ctx` rappelle la règle (par exemple `min_length: 2`). S'il y a plusieurs erreurs, elles apparaissent toutes dans la même réponse.

### Partie 3 : différence entre PUT et PATCH, et idempotence

PUT remplace le livre au complet : il faut envoyer tous les champs obligatoires, et un champ facultatif qu'on n'envoie pas (comme l'ISBN) est effacé. PATCH ne change que les champs envoyés et laisse les autres intacts. PUT est idempotent : envoyer la même demande une fois ou dix fois donne le même résultat final. DELETE l'est aussi : après la première suppression le livre n'existe plus, et les demandes suivantes ne changent plus rien (seule la réponse change, 404 au lieu de 204). POST n'est pas idempotent : chaque demande crée un nouveau livre avec un nouvel `id`, donc répéter la demande crée des doublons.
