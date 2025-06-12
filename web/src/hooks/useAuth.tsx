// src/hooks/useAuth.tsx
import { createContext, useContext, useEffect, useState } from "react";

type AuthContextType = {
  isAutenticado: boolean;
  login: () => void;
  logout: () => void;
  carregando: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAutenticado, setAutenticado] = useState(false);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/me", {
      credentials: "include",
    })
      .then((res) => {
        setAutenticado(res.ok);
        setCarregando(false);
      })
      .catch(() => {
        setAutenticado(false);
        setCarregando(false);
      });
  }, []);

  const login = () => setAutenticado(true);
  const logout = () => setAutenticado(false);

  return (
    <AuthContext.Provider value={{ isAutenticado, login, logout, carregando }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro do AuthProvider");
  return ctx;
};
