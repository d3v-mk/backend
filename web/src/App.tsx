// src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Importa tudo do admin pelo index.ts que você tem, centralizando
import {
  AdminLayout,
  CriarPromotorPage,
  GerenciarCargo,
  DashboardPage,
  ListarPromotores,
  ManutencaoPage,
  NoticiasPage,
} from "./PainelAdmin";


// Promotor
import { 
  PromotorLayout 
} from"./PainelPromotor";

// Outros imports
import HomePage from "./home/pages/HomePage";
import { HomeLayout } from "./home/layout/HomeLayout";
import { RotaPrivada } from "./components/RotaPrivada";
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
              <RotaPrivada>
                <AdminLayout />
              </RotaPrivada>
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
              <RotaPrivada>
                <PromotorLayout />
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