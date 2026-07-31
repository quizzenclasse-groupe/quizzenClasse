// src/pages/QuestionnaireDetail.jsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";

export default function QuestionnaireDetail() {
  const { questionnaireId } = useParams();
  const [questionnaire, setQuestionnaire] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [erreur, setErreur] = useState(null);

  // --- Formulaire d'ajout de question ------------------------------------
  const [enonce, setEnonce] = useState("");
  const [propositions, setPropositions] = useState([
    { libelle: "", est_correcte: true },
    { libelle: "", est_correcte: false },
  ]);
  const [enCoursQuestion, setEnCoursQuestion] = useState(false);

  // --- Formulaire de création de session ----------------------------------
  const [nomSession, setNomSession] = useState("");
  const [modeSession, setModeSession] = useState("individuel");
  const [enCoursSession, setEnCoursSession] = useState(false);

  const charger = () => {
    api
      .get(`/api/questionnaires/${questionnaireId}`)
      .then(setQuestionnaire)
      .catch((e) => setErreur(e.message));
    api
      .get(`/api/questionnaires/${questionnaireId}/sessions`)
      .then(setSessions)
      .catch((e) => setErreur(e.message));
  };

  useEffect(() => {
    charger();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questionnaireId]);

  const majProposition = (index, champ) => (e) => {
    const valeur = champ === "est_correcte" ? e.target.checked : e.target.value;
    setPropositions((props) =>
      props.map((p, i) => (i === index ? { ...p, [champ]: valeur } : p))
    );
  };

  const ajouterLignePropositon = () =>
    setPropositions((props) => [...props, { libelle: "", est_correcte: false }]);

  const ajouterQuestion = async (e) => {
    e.preventDefault();
    setErreur(null);
    setEnCoursQuestion(true);
    try {
      await api.post(`/api/questionnaires/${questionnaireId}/questions`, {
        enonce,
        type_question: "QCM",
        propositions: propositions.filter((p) => p.libelle.trim() !== ""),
      });
      setEnonce("");
      setPropositions([
        { libelle: "", est_correcte: true },
        { libelle: "", est_correcte: false },
      ]);
      charger();
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCoursQuestion(false);
    }
  };

  const creerSession = async (e) => {
    e.preventDefault();
    setErreur(null);
    setEnCoursSession(true);
    try {
      await api.post("/api/sessions", {
        nom_session: nomSession,
        mode: modeSession,
        questionnaire_id: Number(questionnaireId),
      });
      setNomSession("");
      charger();
    } catch (e) {
      setErreur(e.message);
    } finally {
      setEnCoursSession(false);
    }
  };

  const statutSession = (s) => {
    if (s.date_fin) return { texte: "Clôturée", classe: "etiquette--cloture" };
    if (s.date_debut) return { texte: "En cours", classe: "etiquette--cours" };
    return { texte: "Planifiée", classe: "etiquette--attente" };
  };

  if (!questionnaire) {
    return erreur ? <div className="message-erreur">{erreur}</div> : <p className="etat-vide">Chargement…</p>;
  }

  return (
    <div>
      <p className="fil-ariane">
        <Link to="/questionnaires">← Questionnaires</Link>
      </p>
      <h1>{questionnaire.titre}</h1>
      <p style={{ color: "var(--gris-discret)" }}>
        {questionnaire.matiere || "Matière non précisée"}
        {questionnaire.difficulte ? ` · ${questionnaire.difficulte}` : ""}
      </p>

      {erreur && <div className="message-erreur">{erreur}</div>}

      <h2>Questions ({questionnaire.questions.length})</h2>
      <div className="liste-questions">
        {questionnaire.questions.map((q, index) => (
          <div key={q.id} className="carte">
            <strong>
              {index + 1}. {q.enonce}
            </strong>
            <div style={{ marginTop: "0.6rem" }}>
              {q.propositions.map((p) => (
                <div
                  key={p.id}
                  className={`proposition-ligne ${p.est_correcte ? "proposition-ligne--correcte" : ""}`}
                >
                  {p.est_correcte ? "✓" : "○"} {p.libelle}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="carte">
        <h2>Ajouter une question</h2>
        <form onSubmit={ajouterQuestion}>
          <div className="champ">
            <label htmlFor="enonce">Énoncé</label>
            <textarea
              id="enonce"
              rows={2}
              value={enonce}
              onChange={(e) => setEnonce(e.target.value)}
              required
            />
          </div>

          <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--encre-douce)" }}>
            Propositions (cocher la ou les bonnes réponses)
          </label>
          {propositions.map((p, index) => (
            <div key={index} className="proposition-ligne">
              <input
                type="checkbox"
                checked={p.est_correcte}
                onChange={majProposition(index, "est_correcte")}
              />
              <input
                value={p.libelle}
                onChange={majProposition(index, "libelle")}
                placeholder={`Proposition ${index + 1}`}
                style={{
                  flex: 1,
                  padding: "0.4rem 0.6rem",
                  border: "1px solid var(--regle-bleue-claire)",
                  borderRadius: 4,
                }}
              />
            </div>
          ))}
          <button
            type="button"
            className="bouton bouton--discret bouton--petit"
            onClick={ajouterLignePropositon}
            style={{ marginTop: "0.5rem", marginBottom: "1rem" }}
          >
            + Ajouter une proposition
          </button>
          <div>
            <button type="submit" className="bouton bouton--primaire" disabled={enCoursQuestion}>
              Ajouter la question
            </button>
          </div>
        </form>
      </div>

      <h2>Sessions</h2>
      <div className="carte">
        <form onSubmit={creerSession} className="ligne-champs">
          <div className="champ">
            <label htmlFor="nom_session">Nom de la session</label>
            <input
              id="nom_session"
              value={nomSession}
              onChange={(e) => setNomSession(e.target.value)}
              placeholder="ex : Contrôle du 12/07"
              required
            />
          </div>
          <div className="champ">
            <label htmlFor="mode_session">Mode</label>
            <select id="mode_session" value={modeSession} onChange={(e) => setModeSession(e.target.value)}>
              <option value="individuel">Individuel</option>
              <option value="equipe">Équipe</option>
            </select>
          </div>
          <button type="submit" className="bouton bouton--primaire" disabled={enCoursSession}>
            Créer la session
          </button>
        </form>
      </div>

      {sessions.length === 0 ? (
        <p className="etat-vide">Aucune session pour ce questionnaire.</p>
      ) : (
        <div className="grille-cartes">
          {sessions.map((s) => {
            const statut = statutSession(s);
            return (
              <Link key={s.id} to={`/sessions/${s.id}`} className="carte carte-cliquable">
                <h3>{s.nom_session}</h3>
                <span className={`etiquette ${statut.classe}`}>{statut.texte}</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
