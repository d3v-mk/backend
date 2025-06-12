// src/components/RotaPrivada.tsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function RotaPrivada({ children }: { children: React.ReactNode }) {
  const { isAutenticado, carregando } = useAuth();
  const location = useLocation();

  if (carregando) {
    return <div className="text-center text-white p-10">Carregando...</div>;
  }

  if (!isAutenticado) {
    return (
      <Navigate
        to={`/login?next=${encodeURIComponent(location.pathname)}`}
        replace
      />
    );
  }

  return <>{children}</>;
}
