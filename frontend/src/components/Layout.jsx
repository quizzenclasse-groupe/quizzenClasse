// src/components/Layout.jsx
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { enseignant, deconnecter } = useAuth();

  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="top-bar__marque">
          Quizzen<span>Classe</span>
        </div>
        <nav className="top-bar__nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "actif" : "")}>
            Tableau de bord
          </NavLink>
          <NavLink to="/niveaux" className={({ isActive }) => (isActive ? "actif" : "")}>
            Niveaux &amp; élèves
          </NavLink>
          <NavLink
            to="/questionnaires"
            className={({ isActive }) => (isActive ? "actif" : "")}
          >
            Questionnaires
          </NavLink>
          {enseignant && (
            <>
              <span style={{ color: "var(--gris-discret)" }}>
                {enseignant.prenom || enseignant.nom_utilisateur}
              </span>
              <button className="bouton bouton--discret bouton--petit" onClick={deconnecter}>
                Se déconnecter
              </button>
            </>
          )}
        </nav>
      </header>
      <main className="contenu-principal">
        <Outlet />
      </main>
    </div>
  );
}
