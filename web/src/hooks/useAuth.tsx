import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type AuthContextType = {
  isAutenticado: boolean;
  login: () => Promise<void>;
  logout: () => void;
  carregando: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAutenticado, setAutenticado] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const navigate = useNavigate();

  // Verifica autenticação logo que o app carrega
  useEffect(() => {
    verificarAuth();
  }, []);

  const verificarAuth = async () => {
    try {
      const res = await fetch("http://localhost:8000/me", {
        credentials: "include",
      });

      setAutenticado(res.ok);
    } catch {
      setAutenticado(false);
    } finally {
      setCarregando(false);
    }
  };

  const login = async () => {
    // Refaz o check com o cookie recém setado
    await verificarAuth();
  };

  const logout = async () => {
    try {
      await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Erro ao fazer logout:", err);
    } finally {
      setAutenticado(false);
      navigate("/login");
    }
  };

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
