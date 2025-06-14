import { useEffect, useState } from "react";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect"; // ajusta o path se necessário

export default function SacarPage() {
  const [idJogador, setIdJogador] = useState("");
  const [valor, setValor] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [bloqueado, setBloqueado] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    fetch(`${API_URL}/promotor/info`, {
      method: "GET",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Falha ao carregar status");
        return res.json();
      })
      .then((data) => {
        setBloqueado(data.bloqueado ?? false);
      })
      .catch((err) => {
        console.error("Erro ao buscar status:", err);
        setBloqueado(false);
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (bloqueado) return;

    setEnviando(true);
    setMensagem("");

    try {
      const response = await fetch(`${API_URL}/painel/promotor/solicitar_saque`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_publico: idJogador,
          valor: valor,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erro ao solicitar saque");
      }

      setMensagem(data.msg || "Saque solicitado com sucesso!");
    } catch (err: any) {
      setMensagem(err.message || "Erro desconhecido");
      console.error(err);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Fundo animado */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo */}
      <div className="relative z-10 max-w-xl mx-auto mt-10 p-6 rounded-lg shadow-md bg-[#0b1a3d] bg-opacity-90">
        <h1 className="text-2xl font-bold mb-6 text-white text-center">📤 Solicitar Saque</h1>

        {bloqueado && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded font-semibold text-center">
            🚫 Sua conta está bloqueada. Não é possível solicitar saques no momento.
          </div>
        )}

        {mensagem && (
          <div className="mb-4 p-3 bg-blue-100 text-blue-700 rounded text-center">
            {mensagem}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="idJogador" className="block font-medium text-gray-300 mb-1">
              ID Público do Jogador
            </label>
            <input
              type="text"
              id="idJogador"
              value={idJogador}
              onChange={(e) => setIdJogador(e.target.value)}
              required
              disabled={bloqueado}
              className="w-full border border-gray-600 bg-gray-900 text-white px-3 py-2 rounded-md focus:outline-none focus:ring focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-700 disabled:text-gray-400"
            />
          </div>

          <div>
            <label htmlFor="valor" className="block font-medium text-gray-300 mb-1">
              Valor do Saque (ex: 10.00)
            </label>
            <input
              type="number"
              step="0.01"
              id="valor"
              value={valor}
              onChange={(e) => setValor(e.target.value)}
              required
              disabled={bloqueado}
              className="w-full border border-gray-600 bg-gray-900 text-white px-3 py-2 rounded-md focus:outline-none focus:ring focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-700 disabled:text-gray-400"
            />
          </div>

          <div className="flex justify-center">
            <button
              type="submit"
              disabled={enviando || bloqueado}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {enviando ? "Enviando..." : "Solicitar Saque"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
