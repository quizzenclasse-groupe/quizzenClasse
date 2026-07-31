// src/pages/Questionnaires.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function Questionnaires() {
  const [questionnaires, setQuestionnaires] = useState([]);
  const [erreur, setErreur] = useState(null);
  const [formulaire, setFormulaire] = useState({ titre: "", matiere: "", difficulte: "" });
  const [enCours, setEnCours] = useState(false);

  const charger = () =>
    api.get("/api/questionnaires").then(setQuestionnaires).catch((e) => setErreur(e.message));

  useEffect(() => {
    charger();
  }, []);

  const majChamp = (champ) => (e) => setFormulaire((f) => ({ ...f, [champ]: e.target.value }));

  const creer = async (e) => {
    e.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await api.post("/api/questionnaires", { ...formulaire, questions: [] });
      setFormulaire({ titre: "", matiere: "", difficulte: "" });
      charger();
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCours(false);
    }
  };

  return (
    <div>
      <h1>Questionnaires</h1>
      <p className="fil-ariane">
        Créez un questionnaire, puis ajoutez ses questions depuis sa page de détail.
      </p>

      {erreur && <div className="message-erreur">{erreur}</div>}

      <div className="carte">
        <h2>Nouveau questionnaire</h2>
        <form onSubmit={creer} className="ligne-champs">
          <div className="champ">
            <label htmlFor="titre">Titre</label>
            <input id="titre" value={formulaire.titre} onChange={majChamp("titre")} required />
          </div>
          <div className="champ">
            <label htmlFor="matiere">Matière</label>
            <input id="matiere" value={formulaire.matiere} onChange={majChamp("matiere")} />
          </div>
          <div className="champ">
            <label htmlFor="difficulte">Difficulté</label>
            <select id="difficulte" value={formulaire.difficulte} onChange={majChamp("difficulte")}>
              <option value="">—</option>
              <option value="facile">Facile</option>
              <option value="moyen">Moyen</option>
              <option value="difficile">Difficile</option>
            </select>
          </div>
          <button type="submit" className="bouton bouton--primaire" disabled={enCours}>
            Créer
          </button>
        </form>
      </div>

      {questionnaires.length === 0 ? (
        <p className="etat-vide">Aucun questionnaire créé pour le moment.</p>
      ) : (
        <div className="grille-cartes">
          {questionnaires.map((q) => (
            <Link key={q.id} to={`/questionnaires/${q.id}`} className="carte carte-cliquable">
              <h3>{q.titre}</h3>
              <p style={{ color: "var(--gris-discret)", fontSize: "0.85rem" }}>
                {q.matiere || "Matière non précisée"} · {q.nombre_questions} question(s)
              </p>
              {q.difficulte && <span className="etiquette">{q.difficulte}</span>}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
