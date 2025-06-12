import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AdminLayout } from "./admin/layout/AdminLayout";
import CriarPromotorPage from "./admin/pages/CriarPromotorPage";
import GerenciarCargo from "./admin/pages/GerenciarCargo";
import { ListarPromotores } from "./admin/pages/ListarPromotores";
import HomePage from "./home/pages/HomePage";
import { HomeLayout } from "./home/layout/HomeLayout";
import { RotaPrivada } from "./components/RotaPrivada";
import LoginPage from "./pages/LoginPage";
import { AuthProvider } from "./hooks/useAuth";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Home */}
          <Route path="/" element={<HomeLayout />}>
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
          </Route>

          {/* Admin com proteção */}
          <Route
            path="/admin"
            element={
              <RotaPrivada>
                <AdminLayout />
              </RotaPrivada>
            }
          >
            <Route path="criar" element={<CriarPromotorPage />} />
            <Route path="cargos" element={<GerenciarCargo />} />
            <Route path="lista" element={<ListarPromotores />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
