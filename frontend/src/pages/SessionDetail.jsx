// src/pages/SessionDetail.jsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";


export default function SessionDetail() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [participations, setParticipations] = useState([]);
  const [elevesDisponibles, setElevesDisponibles] = useState([]);
  const [statistiques, setStatistiques] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [codePartage, setCodePartage] = useState(null);
  const [lienCopie, setLienCopie] = useState(false);


  const [eleveChoisi, setEleveChoisi] = useState("");
  const [notes, setNotes] = useState({}); // { participationId: score }


  const chargerSession = async () => {
    try {
      const parts = await api.get(`/api/sessions/${sessionId}/participations`);
      setParticipations(parts);
    } catch (e) {
      setErreur(e.message);
    }
  };


  const chargerEleves = async () => {
    try {
      const niveaux = await api.get("/api/niveaux");
      const listes = await Promise.all(
        niveaux.map((n) => api.get(`/api/niveaux/${n.id}/eleves`))
      );
      const tousLesEleves = listes.flat().map((e) => ({
        id: e.id,
        nom: `${e.prenom} ${e.nom_eleve}`,
      }));
      setElevesDisponibles(tousLesEleves);
    } catch (e) {
      setErreur(e.message);
    }
  };


  const chargerStatistiques = async () => {
    try {
      const stats = await api.get(`/api/sessions/${sessionId}/statistiques`);
      setStatistiques(stats);
    } catch {
      // Pas grave si indisponible (ex. droits) : on masque juste le bloc.
    }
  };


  const chargerSessionInfo = async () => {
    try {
      const s = await api.get(`/api/sessions/${sessionId}`);
      setSession(s);
    } catch (e) {
      setErreur(e.message);
    }
  };


  const chargerCodePartage = async () => {
    try {
      const { code } = await api.get(`/api/sessions/${sessionId}/code-partage`);
      setCodePartage(code);
    } catch {
      // Pas grave : le bloc restera masqué.
    }
  };


  useEffect(() => {
    chargerSessionInfo();
    chargerSession();
    chargerEleves();
    chargerStatistiques();
    chargerCodePartage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);


  const demarrer = async () => {
    setErreur(null);
    try {
      const s = await api.post(`/api/sessions/${sessionId}/demarrer`);
      setSession(s);
    } catch (e) {
      setErreur(e.message);
    }
  };


  const copierLien = () => {
    const lien = `${window.location.origin}/participer/${sessionId}/${codePartage}`;
    navigator.clipboard.writeText(lien);
    setLienCopie(true);
    setTimeout(() => setLienCopie(false), 2000);
  };


  const cloturer = async () => {
    setErreur(null);
    try {
      const s = await api.post(`/api/sessions/${sessionId}/cloturer`);
      setSession(s);
      chargerStatistiques();
    } catch (e) {
      setErreur(e.message);
    }
  };


  const inscrire = async (e) => {
    e.preventDefault();
    if (!eleveChoisi) return;
    setErreur(null);
    try {
      await api.post(`/api/sessions/${sessionId}/participations`, {
        participant_id: Number(eleveChoisi),
      });
      setEleveChoisi("");
      chargerSession();
    } catch (e) {
      setErreur(e.message);
    }
  };


  const evaluer = async (participationId) => {
    const score = notes[participationId];
    if (score === undefined || score === "") return;
    setErreur(null);
    try {
      await api.patch(`/api/participations/${participationId}/evaluer`, {
        score: Number(score),
      });
      chargerSession();
      chargerStatistiques();
    } catch (e) {
      setErreur(e.message);
    }
  };


  const etiquetteStatut = {
    planifiee: { texte: "Planifiée", classe: "etiquette--attente" },
    en_cours: { texte: "En cours", classe: "etiquette--cours" },
    cloturee: { texte: "Clôturée", classe: "etiquette--cloture" },
  };


  return (
    <div>
      <h1>
        {session ? session.nom_session : `Session #${sessionId}`}{" "}
        {session && (
          <span className={`etiquette ${etiquetteStatut[session.statut].classe}`}>
            {etiquetteStatut[session.statut].texte}
          </span>
        )}
      </h1>


      {erreur && <div className="message-erreur">{erreur}</div>}


      <div className="carte">
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            className="bouton bouton--primaire"
            onClick={demarrer}
            disabled={session && session.statut !== "planifiee"}
          >
            Démarrer la session
          </button>
          <button
            className="bouton bouton--danger"
            onClick={cloturer}
            disabled={session && session.statut !== "en_cours"}
          >
            Clôturer la session
          </button>
        </div>
      </div>


      {session && session.statut === "en_cours" && codePartage && (
        <div className="carte" style={{ borderColor: "var(--craie-verte)" }}>
          <h2>Lien à partager avec les élèves</h2>
          <p style={{ color: "var(--gris-discret)" }}>
            Chaque élève ouvre ce lien depuis son téléphone ou ordinateur, choisit
            son nom dans la liste et répond directement. La note est calculée
            automatiquement.
          </p>
          <code
            style={{
              display: "block",
              padding: "0.6rem 0.8rem",
              background: "#f2f2f2",
              borderRadius: 4,
              marginBottom: "0.75rem",
              wordBreak: "break-all",
            }}
          >
            {window.location.origin}/participer/{sessionId}/{codePartage}
          </code>
          <button className="bouton bouton--primaire bouton--petit" onClick={copierLien}>
            {lienCopie ? "Copié !" : "Copier le lien"}
          </button>
        </div>
      )}


      {statistiques && (
        <div className="carte">
          <h2>Statistiques</h2>
          <div className="stat-grille">
            <div className="stat-bloc">
              <div className="stat-bloc__valeur">{statistiques.nombre_participations}</div>
              <div className="stat-bloc__label">Participants</div>
            </div>
            <div className="stat-bloc">
              <div className="stat-bloc__valeur">{statistiques.moyenne.toFixed(1)}</div>
              <div className="stat-bloc__label">Moyenne</div>
            </div>
            <div className="stat-bloc">
              <div className="stat-bloc__valeur">{statistiques.taux_reussite.toFixed(0)}%</div>
              <div className="stat-bloc__label">Taux de réussite</div>
            </div>
          </div>
        </div>
      )}


      <h2>Participants</h2>
      <div className="carte">
        <form onSubmit={inscrire} className="ligne-champs">
          <div className="champ">
            <label htmlFor="eleve">Inscrire un élève</label>
            <select id="eleve" value={eleveChoisi} onChange={(e) => setEleveChoisi(e.target.value)}>
              <option value="">— Choisir un élève —</option>
              {elevesDisponibles.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.nom}
                </option>
              ))}
            </select>
          </div>
          <button type="submit" className="bouton bouton--primaire">
            Inscrire
          </button>
        </form>
      </div>


      {participations.length === 0 ? (
        <p className="etat-vide">Aucun participant inscrit pour le moment.</p>
      ) : (
        <table className="tableau-donnees">
          <thead>
            <tr>
              <th>Participant (id)</th>
              <th>Score</th>
              <th>Noter</th>
            </tr>
          </thead>
          <tbody>
            {participations.map((p) => (
              <tr key={p.id}>
                <td>#{p.participant_id}</td>
                <td className="score">{p.score ?? "—"}</td>
                <td style={{ display: "flex", gap: "0.5rem" }}>
                  <input
                    type="number"
                    min="0"
                    step="0.5"
                    style={{ width: 80 }}
                    value={notes[p.id] ?? ""}
                    onChange={(e) => setNotes((n) => ({ ...n, [p.id]: e.target.value }))}
                  />
                  <button className="bouton bouton--discret bouton--petit" onClick={() => evaluer(p.id)}>
                    Valider
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
