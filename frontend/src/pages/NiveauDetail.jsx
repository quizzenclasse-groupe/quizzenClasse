// src/pages/NiveauDetail.jsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";

export default function NiveauDetail() {
  const { niveauId } = useParams();
  const [eleves, setEleves] = useState([]);
  const [erreur, setErreur] = useState(null);
  const [formulaire, setFormulaire] = useState({ nom: "", prenom: "", redoublant: false });
  const [enCours, setEnCours] = useState(false);

  const chargerEleves = () =>
    api
      .get(`/api/niveaux/${niveauId}/eleves`)
      .then(setEleves)
      .catch((e) => setErreur(e.message));

  useEffect(() => {
    chargerEleves();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [niveauId]);

  const majChamp = (champ) => (e) =>
    setFormulaire((f) => ({
      ...f,
      [champ]: e.target.type === "checkbox" ? e.target.checked : e.target.value,
    }));

  const ajouterEleve = async (e) => {
    e.preventDefault();
    setErreur(null);
    setEnCours(true);
    try {
      await api.post("/api/eleves", {
        ...formulaire,
        niveau_ids: [Number(niveauId)],
      });
      setFormulaire({ nom: "", prenom: "", redoublant: false });
      chargerEleves();
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCours(false);
    }
  };

  return (
    <div>
      <p className="fil-ariane">
        <Link to="/niveaux">← Niveaux</Link>
      </p>
      <h1>Élèves du niveau</h1>

      {erreur && <div className="message-erreur">{erreur}</div>}

      <div className="carte">
        <h2>Ajouter un élève</h2>
        <form onSubmit={ajouterEleve} className="ligne-champs">
          <div className="champ">
            <label htmlFor="prenom">Prénom</label>
            <input id="prenom" value={formulaire.prenom} onChange={majChamp("prenom")} required />
          </div>
          <div className="champ">
            <label htmlFor="nom">Nom</label>
            <input id="nom" value={formulaire.nom} onChange={majChamp("nom")} required />
          </div>
          <div className="champ" style={{ justifyContent: "center" }}>
            <label>
              <input
                type="checkbox"
                checked={formulaire.redoublant}
                onChange={majChamp("redoublant")}
              />{" "}
              Redoublant
            </label>
          </div>
          <button type="submit" className="bouton bouton--primaire" disabled={enCours}>
            Ajouter
          </button>
        </form>
      </div>

      {eleves.length === 0 ? (
        <p className="etat-vide">Aucun élève dans ce niveau pour le moment.</p>
      ) : (
        <table className="tableau-donnees">
          <thead>
            <tr>
              <th>Prénom</th>
              <th>Nom</th>
              <th>Redoublant</th>
            </tr>
          </thead>
          <tbody>
            {eleves.map((eleve) => (
              <tr key={eleve.id}>
                <td>{eleve.prenom}</td>
                <td>{eleve.nom_eleve}</td>
                <td>{eleve.redoublant ? "Oui" : "Non"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
