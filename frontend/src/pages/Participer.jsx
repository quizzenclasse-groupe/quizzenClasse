// src/pages/Participer.jsx
//
// Page PUBLIQUE : accessible sans compte, via le lien
// /participer/:sessionId/:code partagé par l'enseignant (affiché au
// tableau, envoyé par mail, etc.). L'élève se désigne dans la liste des
// participants déjà inscrits par l'enseignant, répond au questionnaire,
// et reçoit sa note aussitôt (correction automatique côté serveur).
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";


export default function Participer() {
  const { sessionId, code } = useParams();


  const [donnees, setDonnees] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [participationId, setParticipationId] = useState("");
  const [reponses, setReponses] = useState({}); // { questionId: Set(propositionId) }
  const [resultat, setResultat] = useState(null);
  const [enCours, setEnCours] = useState(false);


  useEffect(() => {
    api
      .get(`/api/public/sessions/${sessionId}/${code}`)
      .then(setDonnees)
      .catch((e) => setErreur(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, code]);


  const basculerProposition = (questionId, propositionId) => {
    setReponses((r) => {
      const ensembleActuel = new Set(r[questionId] || []);
      if (ensembleActuel.has(propositionId)) {
        ensembleActuel.delete(propositionId);
      } else {
        ensembleActuel.add(propositionId);
      }
      return { ...r, [questionId]: ensembleActuel };
    });
  };


  const soumettre = async (e) => {
    e.preventDefault();
    if (!participationId) {
      setErreur("Choisis ton nom dans la liste avant de valider.");
      return;
    }
    setErreur(null);
    setEnCours(true);
    try {
      const corps = {
        participation_id: Number(participationId),
        reponses: donnees.questions.map((q) => ({
          question_id: q.id,
          proposition_ids: Array.from(reponses[q.id] || []),
        })),
      };
      const r = await api.post(
        `/api/public/sessions/${sessionId}/${code}/reponses`,
        corps
      );
      setResultat(r);
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCours(false);
    }
  };


  if (erreur && !donnees) {
    return (
      <div className="page-connexion">
        <div className="carte page-connexion__carte">
          <div className="message-erreur">{erreur}</div>
        </div>
      </div>
    );
  }


  if (!donnees) {
    return <p className="etat-vide">Chargement du questionnaire…</p>;
  }


  if (resultat) {
    return (
      <div className="page-connexion">
        <div className="carte page-connexion__carte" style={{ width: 420, textAlign: "center" }}>
          <h1 className="page-connexion__titre">Réponses envoyées !</h1>
          <div className="stat-bloc">
            <div className="stat-bloc__valeur" style={{ fontSize: "2.4rem" }}>
              {resultat.score_sur_20} / 20
            </div>
            <div className="stat-bloc__label">
              {resultat.nombre_correctes} / {resultat.nombre_questions} bonnes réponses
            </div>
          </div>
          <p style={{ color: "var(--gris-discret)", marginTop: "1rem" }}>
            Tu peux fermer cette page.
          </p>
        </div>
      </div>
    );
  }


  return (
    <div className="contenu-principal" style={{ maxWidth: 640 }}>
      <h1>{donnees.titre_questionnaire}</h1>
      <p className="fil-ariane">{donnees.nom_session}</p>


      {erreur && <div className="message-erreur">{erreur}</div>}


      {donnees.participants_en_attente.length === 0 ? (
        <p className="etat-vide">
          Plus aucun participant en attente : as-tu déjà répondu ?
        </p>
      ) : (
        <form onSubmit={soumettre}>
          <div className="carte">
            <div className="champ">
              <label htmlFor="participant">C'est toi ?</label>
              <select
                id="participant"
                value={participationId}
                onChange={(e) => setParticipationId(e.target.value)}
                required
              >
                <option value="">— Choisis ton nom —</option>
                {donnees.participants_en_attente.map((p) => (
                  <option key={p.participation_id} value={p.participation_id}>
                    {p.nom_affiche}
                  </option>
                ))}
              </select>
            </div>
          </div>


          <div className="liste-questions">
            {donnees.questions.map((q, index) => (
              <div key={q.id} className="carte">
                <strong>
                  {index + 1}. {q.enonce}
                </strong>
                <div style={{ marginTop: "0.6rem" }}>
                  {q.propositions.map((p) => (
                    <label key={p.id} className="proposition-ligne" style={{ cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={(reponses[q.id] || new Set()).has(p.id)}
                        onChange={() => basculerProposition(q.id, p.id)}
                      />
                      {p.libelle}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>


          <button
            type="submit"
            className="bouton bouton--primaire"
            style={{ width: "100%", marginTop: "1rem" }}
            disabled={enCours}
          >
            {enCours ? "Envoi…" : "Valider mes réponses"}
          </button>
        </form>
      )}
    </div>
  );
}
