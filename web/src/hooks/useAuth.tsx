// src/hooks/useAuth.ts
import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type Usuario = {
  id: string;
  nome: string;
  is_admin: boolean;
  is_promoter: boolean;
  avatar_url: string;
};

type AuthContextType = {
  user: Usuario | null;
  login: () => Promise<void>;
  logout: () => void;
  carregando: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    verificarAuth();
  }, []);

  const verificarAuth = async () => {
    try {
      const res = await fetch(`${API_URL}/me`, { credentials: "include" });

      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setCarregando(false);
    }
  };

  const login = async () => {
    await verificarAuth();
  };

  const logout = async () => {
    try {
      await fetch(`${API_URL}/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Erro ao fazer logout:", err);
    } finally {
      setUser(null);
      navigate("/login");
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, carregando }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth precisa estar dentro do AuthProvider");
  return ctx;
};
