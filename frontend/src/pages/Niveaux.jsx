// src/pages/Niveaux.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function Niveaux() {
  const [niveaux, setNiveaux] = useState([]);
  const [erreur, setErreur] = useState(null);

  const [nomNiveau, setNomNiveau] = useState("");
  const [rechercheEtab, setRechercheEtab] = useState("");
  const [resultatsEtab, setResultatsEtab] = useState([]);
  const [etablissementChoisi, setEtablissementChoisi] = useState(null);
  const [enCours, setEnCours] = useState(false);

  const chargerNiveaux = () =>
    api.get("/api/niveaux").then(setNiveaux).catch((e) => setErreur(e.message));

  useEffect(() => {
    chargerNiveaux();
  }, []);

  const rechercherEtablissement = async (e) => {
    e.preventDefault();
    if (!rechercheEtab.trim()) return;
    try {
      const resultats = await api.get(
        `/api/etablissements?q=${encodeURIComponent(rechercheEtab)}`
      );
      setResultatsEtab(resultats);
    } catch (e) {
      setErreur(e.message);
    }
  };

  const creerNiveau = async (e) => {
    e.preventDefault();
    if (!etablissementChoisi) {
      setErreur("Sélectionnez d'abord un établissement dans les résultats de recherche.");
      return;
    }
    setErreur(null);
    setEnCours(true);
    try {
      await api.post("/api/niveaux", {
        nom_niveau: nomNiveau,
        etablissement_id: etablissementChoisi.id,
      });
      setNomNiveau("");
      setResultatsEtab([]);
      setEtablissementChoisi(null);
      setRechercheEtab("");
      chargerNiveaux();
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCours(false);
    }
  };

  return (
    <div>
      <h1>Niveaux &amp; élèves</h1>
      <p className="fil-ariane">
        Un niveau est rattaché à un établissement (ex. "Terminale S" au Lycée
        Test).
      </p>

      {erreur && <div className="message-erreur">{erreur}</div>}

      <div className="carte">
        <h2>Créer un niveau</h2>
        <form onSubmit={rechercherEtablissement} className="ligne-champs">
          <div className="champ">
            <label htmlFor="recherche_etab">1. Rechercher l'établissement</label>
            <input
              id="recherche_etab"
              value={rechercheEtab}
              onChange={(e) => setRechercheEtab(e.target.value)}
              placeholder="Nom de l'établissement…"
            />
          </div>
          <button type="submit" className="bouton bouton--discret" style={{ height: 42, marginTop: 22 }}>
            Rechercher
          </button>
        </form>

        {resultatsEtab.length > 0 && (
          <div style={{ marginBottom: "1rem" }}>
            {resultatsEtab.map((etab) => (
              <label key={etab.id} style={{ display: "block", marginBottom: 4 }}>
                <input
                  type="radio"
                  name="etablissement"
                  checked={etablissementChoisi?.id === etab.id}
                  onChange={() => setEtablissementChoisi(etab)}
                />{" "}
                {etab.nom_etablissement} ({etab.code_postal})
              </label>
            ))}
          </div>
        )}

        <form onSubmit={creerNiveau} className="ligne-champs">
          <div className="champ">
            <label htmlFor="nom_niveau">2. Nom du niveau</label>
            <input
              id="nom_niveau"
              value={nomNiveau}
              onChange={(e) => setNomNiveau(e.target.value)}
              placeholder="ex : Terminale S"
              required
            />
          </div>
          <button
            type="submit"
            className="bouton bouton--primaire"
            style={{ height: 42, marginTop: 22 }}
            disabled={enCours}
          >
            Créer le niveau
          </button>
        </form>
      </div>

      <h2>Mes niveaux</h2>
      {niveaux.length === 0 ? (
        <p className="etat-vide">Aucun niveau créé pour le moment.</p>
      ) : (
        <div className="grille-cartes">
          {niveaux.map((niveau) => (
            <Link key={niveau.id} to={`/niveaux/${niveau.id}`} className="carte carte-cliquable">
              <h3>{niveau.nom_niveau}</h3>
              <span className="etiquette">{niveau.effectif} élève(s)</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
