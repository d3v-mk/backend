import { useState } from "react";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect"; // ajusta o path se precisar

export default function ManutencaoPage() {
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL;

  async function ativarManutencao() {
    setLoading(true);
    setMensagem(null);
    setErro(null);
    try {
      const res = await fetch(`${API_URL}/admin/ativar-manutencao`, {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) throw new Error("Falha ao ativar manutenção");
      const data = await res.json();
      setMensagem(data.msg);
    } catch (err: any) {
      setErro(err.message || "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  async function encerrarManutencao() {
    setLoading(true);
    setMensagem(null);
    setErro(null);
    try {
      const res = await fetch(`${API_URL}/admin/encerrar-manutencao`, {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) throw new Error("Falha ao encerrar manutenção");
      const data = await res.json();
      setMensagem(
        data.msg +
          (data.mesas_reabertas
            ? ` (Mesas reabertas: ${data.mesas_reabertas.join(", ")})`
            : "")
      );
    } catch (err: any) {
      setErro(err.message || "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden font-sans">
      {/* Fundo animado */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo */}
      <section className="relative z-10 max-w-xl mx-auto p-8 space-y-4">
        <h2 className="text-2xl font-bold">⚙️ Painel de Manutenção</h2>
        <p className="text-gray-300">
          Ative a manutenção para mesas em jogo e abertas, ou encerre a manutenção para reabrir mesas.
        </p>

        <div className="flex gap-4">
          <button
            onClick={ativarManutencao}
            disabled={loading}
            className={`px-6 py-2 rounded ${
              loading ? "bg-red-700 cursor-not-allowed" : "bg-red-600 hover:bg-red-700"
            } text-white font-semibold transition`}
          >
            {loading ? "Processando..." : "Ativar Manutenção"}
          </button>

          <button
            onClick={encerrarManutencao}
            disabled={loading}
            className={`px-6 py-2 rounded ${
              loading ? "bg-green-700 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"
            } text-white font-semibold transition`}
          >
            {loading ? "Processando..." : "Encerrar Manutenção"}
          </button>
        </div>

        {mensagem && (
          <p className="mt-4 text-green-400 font-semibold">{mensagem}</p>
        )}
        {erro && <p className="mt-4 text-red-500 font-semibold">{erro}</p>}
      </section>
    </main>
  );
}
