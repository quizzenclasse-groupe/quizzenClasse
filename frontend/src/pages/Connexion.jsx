// src/pages/Connexion.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Connexion() {
  const { connecter } = useAuth();
  const navigate = useNavigate();

  const [nomUtilisateur, setNomUtilisateur] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState(null);
  const [enCours, setEnCours] = useState(false);

  const soumettre = async (evenement) => {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await connecter(nomUtilisateur, motDePasse);
      navigate("/");
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCours(false);
    }
  };

  return (
    <div className="page-connexion">
      <div className="carte page-connexion__carte">
        <h1 className="page-connexion__titre">QuizzenClasse</h1>

        {erreur && <div className="message-erreur">{erreur}</div>}

        <form onSubmit={soumettre}>
          <div className="champ">
            <label htmlFor="nom_utilisateur">Identifiant</label>
            <input
              id="nom_utilisateur"
              value={nomUtilisateur}
              onChange={(e) => setNomUtilisateur(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="champ">
            <label htmlFor="mot_de_passe">Mot de passe</label>
            <input
              id="mot_de_passe"
              type="password"
              value={motDePasse}
              onChange={(e) => setMotDePasse(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="bouton bouton--primaire"
            style={{ width: "100%" }}
            disabled={enCours}
          >
            {enCours ? "Connexion…" : "Se connecter"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: "1rem", fontSize: "0.9rem" }}>
          Pas encore de compte ? <Link to="/inscription">Créer un compte enseignant</Link>
        </p>
      </div>
    </div>
  );
}
