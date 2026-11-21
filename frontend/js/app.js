// Catalogue de bibliothèque, relié à l'API FastAPI du devoir 2 :
// les livres sont lus, ajoutés, modifiés et supprimés avec fetch (async/await).
// Plus de localStorage ni de data.js : la base de données est côté API.

// Adresse de l'API (uvicorn app.main:app --reload)
const URL_API = "http://127.0.0.1:8000";
const ANNEE_MIN = 1450;
const CHAMPS_FORMULAIRE = ["titre", "auteur", "annee", "categorie"];

// ---------- État de l'application ----------

let livres = [];                // les livres reçus de l'API
let chargementReussi = false;   // faux tant que l'API n'a pas répondu correctement

// ---------- Éléments de la page ----------

const conteneurLivres = document.getElementById("liste-livres");
const champRecherche = document.getElementById("recherche");
const filtreCategorie = document.getElementById("filtre-categorie");
const filtreDisponibles = document.getElementById("filtre-disponibles");
const selectTri = document.getElementById("tri");
const compteur = document.getElementById("compteur");
const messageVide = document.getElementById("message-vide");
const etatApi = document.getElementById("etat-api");
const texteEtatApi = document.getElementById("texte-etat-api");
const boutonReessayer = document.getElementById("bouton-reessayer");
const formulaire = document.getElementById("formulaire-ajout");
const erreurFormulaire = document.getElementById("erreur-formulaire");
const boutonAjouter = formulaire.querySelector('button[type="submit"]');

// ---------- Communication avec l'API ----------

// Envoie une demande à l'API et renvoie la réponse en JSON (null si 204).
// En cas d'échec, lance une Error dont le message est lisible par l'utilisateur.
async function appelerApi(chemin, options = {}) {
  let reponse;
  try {
    reponse = await fetch(`${URL_API}${chemin}`, options);
  } catch {
    // fetch n'échoue (promesse rejetée) que si le serveur est injoignable
    throw new Error(
      "Impossible de joindre l'API. Vérifiez qu'elle est démarrée (uvicorn app.main:app --reload)."
    );
  }

  if (!reponse.ok) {
    throw new Error(await lireMessageErreur(reponse));
  }
  return reponse.status === 204 ? null : reponse.json();
}

// Extrait le message d'une réponse d'erreur de l'API : {"detail": "..."} (404, 409)
// ou {"detail": [{loc, msg, ...}]} (422)
async function lireMessageErreur(reponse) {
  try {
    const corps = await reponse.json();
    if (typeof corps.detail === "string") return corps.detail;
    if (Array.isArray(corps.detail)) {
      return corps.detail.map((e) => `${e.loc[e.loc.length - 1]} : ${e.msg}`).join(" ; ");
    }
  } catch {
    // le corps n'est pas du JSON : on utilise le message général
  }
  return `Erreur ${reponse.status} de l'API.`;
}

// Options d'une demande qui envoie du JSON (POST, PATCH)
function optionsJson(methode, donnees) {
  return {
    method: methode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(donnees)
  };
}

// ---------- Message d'état (chargement ou erreur) ----------

function afficherEtat(type, message, avecBoutonReessayer = false) {
  etatApi.hidden = false;
  etatApi.className = `etat-api etat-api--${type}`; // "chargement" ou "erreur"
  // Une erreur est annoncée tout de suite par le lecteur d'écran
  etatApi.setAttribute("role", type === "erreur" ? "alert" : "status");
  texteEtatApi.textContent = message;
  boutonReessayer.hidden = !avecBoutonReessayer;
}

function cacherEtat() {
  etatApi.hidden = true;
}

// ---------- Chargement des livres ----------

async function chargerLivres() {
  chargementReussi = false;
  afficherEtat("chargement", "Chargement des livres…");
  mettreAJourAffichage();

  try {
    // 100 est la limite maximale de l'API
    livres = await appelerApi("/livres?limit=100");
    chargementReussi = true;
    cacherEtat();
  } catch (erreur) {
    livres = [];
    afficherEtat("erreur", erreur.message, true);
  }
  mettreAJourAffichage();
}

// ---------- Recherche, filtres et tri (sur les livres déjà reçus) ----------

// Met en minuscules et retire les accents : "Étranger" -> "etranger"
function normaliser(texte) {
  return texte
    .normalize("NFD")                 // sépare la lettre et son accent
    .replace(/[̀-ͯ]/g, "")  // supprime les accents
    .toLowerCase();
}

// Garde seulement les livres qui respectent les trois critères en même temps
function filtrerLivres() {
  const recherche = normaliser(champRecherche.value.trim());
  const categorie = filtreCategorie.value;
  const seulementDisponibles = filtreDisponibles.checked;

  return livres.filter((livre) => {
    const texteLivre = normaliser(`${livre.titre} ${livre.auteur}`);
    const correspondRecherche = texteLivre.includes(recherche);
    const correspondCategorie = categorie === "" || livre.categorie === categorie;
    const correspondDispo = !seulementDisponibles || livre.disponible;
    return correspondRecherche && correspondCategorie && correspondDispo;
  });
}

// Renvoie une copie triée (la valeur du select est par ex. "titre-asc")
function trierLivres(liste) {
  const [critere, sens] = selectTri.value.split("-");
  const facteur = sens === "asc" ? 1 : -1;

  return [...liste].sort((a, b) => {
    if (critere === "titre") {
      return a.titre.localeCompare(b.titre, "fr") * facteur;
    }
    return (a.annee - b.annee) * facteur;
  });
}

// ---------- Affichage ----------

// Construit une carte (élément <article>) pour un livre, avec le DOM
function creerCarte(livre) {
  const carte = document.createElement("article");
  carte.className = "carte";

  const titre = document.createElement("h3");
  titre.className = "carte__titre";
  titre.textContent = livre.titre;

  const auteur = document.createElement("p");
  auteur.className = "carte__auteur";
  auteur.textContent = livre.auteur;

  const meta = document.createElement("p");
  meta.className = "carte__meta";
  meta.textContent = `${livre.annee} · ${livre.categorie}`;

  const etiquette = document.createElement("span");
  etiquette.className = livre.disponible
    ? "etiquette etiquette--disponible"
    : "etiquette etiquette--emprunte";
  etiquette.textContent = livre.disponible ? "Disponible" : "Emprunté";

  const boutonEmprunter = document.createElement("button");
  boutonEmprunter.type = "button";
  boutonEmprunter.textContent = "Emprunter";
  boutonEmprunter.disabled = !livre.disponible; // grisé si déjà emprunté
  boutonEmprunter.addEventListener("click", () => emprunterLivre(livre.id));

  const boutonSupprimer = document.createElement("button");
  boutonSupprimer.type = "button";
  boutonSupprimer.className = "bouton-danger";
  boutonSupprimer.textContent = "Supprimer";
  boutonSupprimer.setAttribute("aria-label", `Supprimer ${livre.titre}`);
  boutonSupprimer.addEventListener("click", () => supprimerLivre(livre.id));

  const actions = document.createElement("div");
  actions.className = "carte__actions";
  actions.append(boutonEmprunter, boutonSupprimer);

  carte.append(titre, auteur, meta, etiquette, actions);
  return carte;
}

// Recalcule la liste à afficher et met à jour toute la page
function mettreAJourAffichage() {
  // Pendant le chargement ou si l'API est arrêtée : pas de liste, pas de compteur
  if (!chargementReussi) {
    conteneurLivres.replaceChildren();
    compteur.textContent = "";
    messageVide.hidden = true;
    return;
  }

  const resultats = trierLivres(filtrerLivres());

  conteneurLivres.replaceChildren(...resultats.map(creerCarte));

  const n = resultats.length;
  compteur.textContent = `${n} livre${n > 1 ? "s" : ""} trouvé${n > 1 ? "s" : ""}`;
  messageVide.hidden = n !== 0;
}

// ---------- Actions : emprunter, supprimer ----------

async function emprunterLivre(id) {
  try {
    // PATCH : on envoie seulement le champ à modifier
    const livreMisAJour = await appelerApi(`/livres/${id}`, optionsJson("PATCH", { disponible: false }));
    livres = livres.map((livre) => (livre.id === id ? livreMisAJour : livre));
    cacherEtat();
    mettreAJourAffichage();
  } catch (erreur) {
    afficherEtat("erreur", erreur.message);
  }
}

async function supprimerLivre(id) {
  const livre = livres.find((l) => l.id === id);
  if (!livre) return;

  // confirm() ouvre une boîte Oui/Non ; on s'arrête si l'utilisateur refuse
  if (!confirm(`Supprimer « ${livre.titre} » du catalogue ?`)) return;

  try {
    await appelerApi(`/livres/${id}`, { method: "DELETE" });
    livres = livres.filter((l) => l.id !== id);
    cacherEtat();
    mettreAJourAffichage();
  } catch (erreur) {
    afficherEtat("erreur", erreur.message);
  }
}

// ---------- Formulaire : validation et ajout ----------

// Valeur d'un champ du formulaire, sans espaces au début ni à la fin
function lireChamp(idChamp) {
  return document.getElementById(idChamp).value.trim();
}

// Affiche (ou efface, si message vide) l'erreur sous un champ
function afficherErreur(idChamp, message) {
  document.getElementById(`erreur-${idChamp}`).textContent = message;
  document.getElementById(idChamp).setAttribute("aria-invalid", message ? "true" : "false");
}

// Renvoie un objet { champ: message } ; il est vide si tout est valide
function validerFormulaire() {
  const erreurs = {};
  const anneeCourante = new Date().getFullYear();

  if (lireChamp("titre").length < 2) {
    erreurs.titre = "Le titre est obligatoire (au moins 2 caractères).";
  }
  if (lireChamp("auteur").length < 2) {
    erreurs.auteur = "L'auteur est obligatoire (au moins 2 caractères).";
  }

  const anneeSaisie = lireChamp("annee");
  const annee = Number(anneeSaisie);
  if (anneeSaisie === "" || !Number.isInteger(annee) || annee < ANNEE_MIN || annee > anneeCourante) {
    erreurs.annee = `L'année doit être comprise entre ${ANNEE_MIN} et ${anneeCourante}.`;
  }

  if (lireChamp("categorie") === "") {
    erreurs.categorie = "Veuillez choisir une catégorie.";
  }

  return erreurs;
}

async function ajouterLivre(evenement) {
  evenement.preventDefault(); // empêche le rechargement de la page
  erreurFormulaire.textContent = "";

  const erreurs = validerFormulaire();
  CHAMPS_FORMULAIRE.forEach((id) => afficherErreur(id, erreurs[id] || ""));

  // Au moins une erreur : on met le curseur sur le premier champ fautif
  const premierChampInvalide = CHAMPS_FORMULAIRE.find((id) => erreurs[id]);
  if (premierChampInvalide) {
    document.getElementById(premierChampInvalide).focus();
    return;
  }

  // Évite un double envoi pendant que l'API répond
  boutonAjouter.disabled = true;
  boutonAjouter.textContent = "Ajout en cours…";

  try {
    // POST : l'API génère l'id et renvoie le livre créé
    const nouveauLivre = await appelerApi("/livres", optionsJson("POST", {
      titre: lireChamp("titre"),
      auteur: lireChamp("auteur"),
      annee: Number(lireChamp("annee")),
      categorie: lireChamp("categorie"),
      disponible: document.getElementById("disponible").checked
    }));

    formulaire.reset();
    if (chargementReussi) {
      livres.push(nouveauLivre);
      mettreAJourAffichage();
    } else {
      await chargerLivres(); // l'API vient de répondre : on recharge toute la liste
    }
  } catch (erreur) {
    erreurFormulaire.textContent = erreur.message;
  } finally {
    boutonAjouter.disabled = false;
    boutonAjouter.textContent = "Ajouter le livre";
  }
}

// ---------- Écouteurs d'événements ----------

// "input" se déclenche à chaque lettre tapée : recherche en temps réel
champRecherche.addEventListener("input", mettreAJourAffichage);
filtreCategorie.addEventListener("change", mettreAJourAffichage);
filtreDisponibles.addEventListener("change", mettreAJourAffichage);
selectTri.addEventListener("change", mettreAJourAffichage);
formulaire.addEventListener("submit", ajouterLivre);
boutonReessayer.addEventListener("click", chargerLivres);

// Premier chargement au démarrage de la page
chargerLivres();
