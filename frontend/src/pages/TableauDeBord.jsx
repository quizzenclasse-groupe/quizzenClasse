// src/pages/TableauDeBord.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function TableauDeBord() {
  const [niveaux, setNiveaux] = useState([]);
  const [questionnaires, setQuestionnaires] = useState([]);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    Promise.all([api.get("/api/niveaux"), api.get("/api/questionnaires")])
      .then(([n, q]) => {
        setNiveaux(n);
        setQuestionnaires(q);
      })
      .catch((e) => setErreur(e.message));
  }, []);

  return (
    <div>
      <h1>Tableau de bord</h1>
      <p className="fil-ariane">Vue d'ensemble de votre activité pédagogique.</p>

      {erreur && <div className="message-erreur">{erreur}</div>}

      <div className="stat-grille" style={{ marginBottom: "2rem" }}>
        <div className="carte stat-bloc">
          <div className="stat-bloc__valeur">{niveaux.length}</div>
          <div className="stat-bloc__label">Niveaux</div>
        </div>
        <div className="carte stat-bloc">
          <div className="stat-bloc__valeur">{questionnaires.length}</div>
          <div className="stat-bloc__label">Questionnaires</div>
        </div>
        <div className="carte stat-bloc">
          <div className="stat-bloc__valeur">
            {questionnaires.reduce((total, q) => total + q.nombre_questions, 0)}
          </div>
          <div className="stat-bloc__label">Questions créées</div>
        </div>
      </div>

      <h2>Accès rapide</h2>
      <div className="grille-cartes">
        <Link to="/niveaux" className="carte carte-cliquable">
          <h3>Niveaux &amp; élèves</h3>
          <p>Gérer vos classes, vos élèves et vos équipes.</p>
        </Link>
        <Link to="/questionnaires" className="carte carte-cliquable">
          <h3>Questionnaires</h3>
          <p>Créer et lancer des QCM, suivre les sessions et les résultats.</p>
        </Link>
      </div>
    </div>
  );
}
