// src/components/RotasProtegidas.tsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

type Props = {
  children: React.ReactNode;
};

export function RotaPrivada({ children }: Props) {
  const { user, carregando } = useAuth();
  const location = useLocation();

  if (carregando) return <div className="text-center text-white p-10">Carregando...</div>;

  if (!user) {
    return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return <>{children}</>;
}

export function RotaAdmin({ children }: Props) {
  const { user, carregando } = useAuth();
  const location = useLocation();

  if (carregando) return <div className="text-center text-white p-10">Carregando...</div>;

  if (!user || !user.is_admin) {
    return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return <>{children}</>;
}

export function RotaPromotor({ children }: Props) {
  const { user, carregando } = useAuth();
  const location = useLocation();

  if (carregando) return <div className="text-center text-white p-10">Carregando...</div>;

  if (!user || !user.is_promoter) {
    return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return <>{children}</>;
}
