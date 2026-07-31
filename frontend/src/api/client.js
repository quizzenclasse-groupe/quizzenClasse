// src/api/client.js
//
// Client HTTP minimal (basé sur `fetch`, pas de dépendance type axios,
// pour rester léger) centralisant :
//   - la construction de l'URL de base (VITE_API_URL) ;
//   - l'ajout automatique de l'en-tête `Authorization: Bearer <token>` ;
//   - la gestion uniforme des erreurs HTTP (l'API renvoie toujours
//     `{ "detail": "..." }` en cas d'erreur, cf. FastAPI/HTTPException).

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function lireToken() {
  return localStorage.getItem("quizzenclasse_token");
}

/**
 * Effectue un appel HTTP vers l'API et retourne le JSON décodé.
 * Lève une erreur JS (avec un message lisible) en cas de statut >= 400.
 */
async function requete(chemin, { methode = "GET", corps, avecAuth = true } = {}) {
  const entetes = { "Content-Type": "application/json" };

  if (avecAuth) {
    const token = lireToken();
    if (token) {
      entetes["Authorization"] = `Bearer ${token}`;
    }
  }

  const reponse = await fetch(`${BASE_URL}${chemin}`, {
    method: methode,
    headers: entetes,
    body: corps !== undefined ? JSON.stringify(corps) : undefined,
  });

  // Les réponses 204 (No Content, ex. suppression) n'ont pas de corps JSON.
  if (reponse.status === 204) {
    return null;
  }

  const donnees = await reponse.json().catch(() => null);

  if (!reponse.ok) {
    const message =
      (donnees && (donnees.detail || JSON.stringify(donnees))) ||
      `Erreur HTTP ${reponse.status}`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return donnees;
}

export const api = {
  get: (chemin) => requete(chemin),
  post: (chemin, corps) => requete(chemin, { methode: "POST", corps }),
  patch: (chemin, corps) => requete(chemin, { methode: "PATCH", corps }),
  delete: (chemin) => requete(chemin, { methode: "DELETE" }),

  /**
   * Connexion : utilise le endpoint JSON dédié (`/api/auth/login-json`)
   * plutôt que le formulaire OAuth2 standard, plus simple à consommer
   * depuis React (pas besoin de `URLSearchParams`).
   */
  connecter: (nomUtilisateur, motDePasse) =>
    requete("/api/auth/login-json", {
      methode: "POST",
      corps: { nom_utilisateur: nomUtilisateur, mot_de_passe: motDePasse },
      avecAuth: false,
    }),

  inscrire: (donnees) =>
    requete("/api/auth/register", { methode: "POST", corps: donnees, avecAuth: false }),
};

export { lireToken };
