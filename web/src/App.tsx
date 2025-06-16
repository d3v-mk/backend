import { BrowserRouter, Routes, Route } from "react-router-dom";

import {
  AdminLayout,
  CriarPromotorPage,
  GerenciarCargo,
  DashboardPage,
  ListarPromotores,
  ManutencaoPage,
  NoticiasPage,
} from "./PainelAdmin";

import {
  PromotorLayout,
  SacarPage,
  VerSaquesPage,
  DashBoardPage,
  LojaConfigPage,
} from "./PainelPromotor";

import {
  RankPage
} from "./Rank";

import {
  LojaPromotorLayout

} from "./LojaPromotor";

import HomePage from "./home/pages/HomePage";
import HomeLayout from "./home/layout/HomeLayout";

import { RotaAdmin, RotaPromotor, RotaPrivada } from "./components/RotaPrivada";
import LoginPage from "./pages/LoginPage";
import { AuthProvider } from "./hooks/useAuth";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Home */}
          <Route path="/" element={<HomeLayout />}>
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
          </Route>

          {/* Admin */}
          <Route
            path="/admin"
            element={
              <RotaAdmin>
                <AdminLayout />
              </RotaAdmin>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="criar" element={<CriarPromotorPage />} />
            <Route path="cargos" element={<GerenciarCargo />} />
            <Route path="lista" element={<ListarPromotores />} />
            <Route path="manutencao" element={<ManutencaoPage />} />
            <Route path="noticias" element={<NoticiasPage />} />
          </Route>

          {/* Promotor */}
          <Route
            path="/promotor"
            element={
              <RotaPromotor>
                <PromotorLayout />
              </RotaPromotor>
            }
          >
            <Route index element={<DashBoardPage />} />
            <Route path="saque" element={<SacarPage />} />
            <Route path="saques" element={<VerSaquesPage />} />
            <Route path="loja" element={<LojaConfigPage/>} />
          </Route>

          {/* LojaPromotor */}
          <Route
            path="/loja/:slug"
            element={
              <RotaPrivada>
                <LojaPromotorLayout />
              </RotaPrivada>
            }
          >

          </Route>

          {/* RankPage */}
          <Route
            path="rank"
            element={
              <RotaPrivada>
                <RankPage />
              </RotaPrivada>
            }
          >

          </Route>

        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
