// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import RouteProtegee from "./components/RouteProtegee";
import Layout from "./components/Layout";
import Connexion from "./pages/Connexion";
import Inscription from "./pages/Inscription";
import Participer from "./pages/Participer";
import TableauDeBord from "./pages/TableauDeBord";
import Niveaux from "./pages/Niveaux";
import NiveauDetail from "./pages/NiveauDetail";
import Questionnaires from "./pages/Questionnaires";
import QuestionnaireDetail from "./pages/QuestionnaireDetail";
import SessionDetail from "./pages/SessionDetail";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/connexion" element={<Connexion />} />
          <Route path="/inscription" element={<Inscription />} />
        <Route path="/participer/:sessionId/:code" element={<Participer />} />

          <Route
            element={
              <RouteProtegee>
                <Layout />
              </RouteProtegee>
            }
          >
            <Route path="/" element={<TableauDeBord />} />
            <Route path="/niveaux" element={<Niveaux />} />
            <Route path="/niveaux/:niveauId" element={<NiveauDetail />} />
            <Route path="/questionnaires" element={<Questionnaires />} />
            <Route path="/questionnaires/:questionnaireId" element={<QuestionnaireDetail />} />
            <Route path="/sessions/:sessionId" element={<SessionDetail />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
