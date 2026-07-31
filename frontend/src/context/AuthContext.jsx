// src/context/AuthContext.jsx
//
// Contexte React encapsulant l'état d'authentification côté client :
// le token JWT (persisté dans localStorage pour survivre à un
// rafraîchissement de page) et le profil de l'enseignant connecté.
//
// C'est l'équivalent côté frontend de `ConnexionService` côté backend :
// dans le programme console d'origine, l'utilisateur courant vivait en
// mémoire process (`self._utilisateur_courant`) ; ici, il vit dans le
// state React + localStorage, puisque chaque requête HTTP est sans état
// (le serveur ne "se souvient" de rien entre deux appels).

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

const CLE_TOKEN = "quizzenclasse_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(CLE_TOKEN));
  const [enseignant, setEnseignant] = useState(null);
  const [chargement, setChargement] = useState(true);

  const chargerProfil = useCallback(async () => {
    if (!token) {
      setEnseignant(null);
      setChargement(false);
      return;
    }
    try {
      const profil = await api.get("/api/auth/moi");
      setEnseignant(profil);
    } catch {
      // Token invalide ou expiré : on nettoie l'état d'authentification.
      localStorage.removeItem(CLE_TOKEN);
      setToken(null);
      setEnseignant(null);
    } finally {
      setChargement(false);
    }
  }, [token]);

  useEffect(() => {
    chargerProfil();
  }, [chargerProfil]);

  const connecter = async (nomUtilisateur, motDePasse) => {
    const { access_token } = await api.connecter(nomUtilisateur, motDePasse);
    localStorage.setItem(CLE_TOKEN, access_token);
    setToken(access_token);
  };

  const inscrire = async (donnees) => {
    await api.inscrire(donnees);
    // Après inscription, on connecte directement l'enseignant : évite
    // une étape supplémentaire dans le parcours utilisateur.
    await connecter(donnees.nom_utilisateur, donnees.mot_de_passe);
  };

  const deconnecter = () => {
    localStorage.removeItem(CLE_TOKEN);
    setToken(null);
    setEnseignant(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, enseignant, chargement, connecter, inscrire, deconnecter }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const contexte = useContext(AuthContext);
  if (!contexte) {
    throw new Error("useAuth doit être utilisé à l'intérieur de <AuthProvider>.");
  }
  return contexte;
}
