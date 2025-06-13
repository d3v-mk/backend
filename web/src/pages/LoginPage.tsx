import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth"; // ajusta o path se precisar

export default function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useAuth();

  const nextParam = new URLSearchParams(location.search).get("next");
  const next = nextParam || "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");

  const API_URL = import.meta.env.VITE_API_URL;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro("");

    try {
      const formData = new URLSearchParams({
        username,
        password,
        next,
      });

      const res = await fetch(`${API_URL}/login-web`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (res.ok) {
        // Aguarda login e sincronização com backend
        await login();

        const { next: nextUrl } = await res.json();

        // Espera pequena pra garantir que o navegador fixou o cookie
        setTimeout(() => {
          navigate(nextUrl);
        }, 100);
      } else {
        const err = await res.json();
        setErro(err.detail || "Usuário ou senha inválidos.");
      }
    } catch {
      setErro("Erro de conexão com o servidor.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-zinc-900 to-black text-yellow-400 px-4">
      <div className="bg-zinc-900 p-10 rounded-xl shadow-2xl w-full max-w-md space-y-6">
        <h1 className="text-4xl font-extrabold text-center">
          PanoPoker
          <br />
          Login
        </h1>

        {erro && (
          <div className="text-red-500 text-center font-semibold">{erro}</div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="text"
            name="username"
            placeholder="Usuário"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 rounded bg-black text-yellow-400 placeholder-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <input
            type="password"
            name="password"
            placeholder="Senha"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 rounded bg-black text-yellow-400 placeholder-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <input type="hidden" name="next" value={next} />
          <button
            type="submit"
            className="w-full bg-yellow-400 text-black font-bold py-2 rounded hover:bg-yellow-500 transition"
          >
            Entrar
          </button>
        </form>

        <div className="text-center text-sm text-yellow-500">ou</div>

        <a
          href={`https://accounts.google.com/o/oauth2/v2/auth?client_id=${import.meta.env.VITE_GOOGLE_CLIENT_ID}&redirect_uri=${import.meta.env.VITE_GOOGLE_REDIRECT_URI}&response_type=code&scope=openid email profile&access_type=offline&prompt=consent&state=${encodeURIComponent(
            next
          )}`}
          className="block text-center py-2 rounded bg-white text-black font-bold hover:bg-gray-100 transition"
        >
          Entrar com Google
        </a>
      </div>
    </div>
  );
}
