// src/pages/Inscription.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Inscription() {
  const { inscrire } = useAuth();
  const navigate = useNavigate();

  const [formulaire, setFormulaire] = useState({
    nom_utilisateur: "",
    mot_de_passe: "",
    nom: "",
    prenom: "",
    email: "",
  });
  const [erreur, setErreur] = useState(null);
  const [enCours, setEnCours] = useState(false);

  const majChamp = (champ) => (e) =>
    setFormulaire((f) => ({ ...f, [champ]: e.target.value }));

  const soumettre = async (evenement) => {
    evenement.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await inscrire(formulaire);
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
        <h1 className="page-connexion__titre">Créer un compte</h1>

        {erreur && <div className="message-erreur">{erreur}</div>}

        <form onSubmit={soumettre}>
          <div className="champ">
            <label htmlFor="nom_utilisateur">Identifiant</label>
            <input
              id="nom_utilisateur"
              value={formulaire.nom_utilisateur}
              onChange={majChamp("nom_utilisateur")}
              required
              minLength={3}
              autoFocus
            />
          </div>
          <div className="champ">
            <label htmlFor="mot_de_passe">Mot de passe (8 caractères min.)</label>
            <input
              id="mot_de_passe"
              type="password"
              value={formulaire.mot_de_passe}
              onChange={majChamp("mot_de_passe")}
              required
              minLength={8}
            />
          </div>
          <div className="ligne-champs">
            <div className="champ">
              <label htmlFor="prenom">Prénom</label>
              <input id="prenom" value={formulaire.prenom} onChange={majChamp("prenom")} />
            </div>
            <div className="champ">
              <label htmlFor="nom">Nom</label>
              <input id="nom" value={formulaire.nom} onChange={majChamp("nom")} />
            </div>
          </div>
          <div className="champ">
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              value={formulaire.email}
              onChange={majChamp("email")}
            />
          </div>
          <button
            type="submit"
            className="bouton bouton--primaire"
            style={{ width: "100%" }}
            disabled={enCours}
          >
            {enCours ? "Création…" : "Créer mon compte"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: "1rem", fontSize: "0.9rem" }}>
          Déjà inscrit ? <Link to="/connexion">Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
