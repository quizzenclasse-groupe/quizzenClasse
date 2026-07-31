// src/components/RouteProtegee.jsx
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Enveloppe les routes qui exigent un enseignant connecté. Redirige vers
 * /connexion si aucun token valide n'est présent, une fois le chargement
 * initial du profil terminé (évite un flash de redirection au démarrage).
 */
export default function RouteProtegee({ children }) {
  const { token, chargement } = useAuth();

  if (chargement) {
    return <p className="etat-vide">Chargement…</p>;
  }

  if (!token) {
    return <Navigate to="/connexion" replace />;
  }

  return children;
}
