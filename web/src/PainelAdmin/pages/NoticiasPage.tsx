import { useState } from "react";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";

export default function NoticiasPage() {
  const [mensagem, setMensagem] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const API_URL = import.meta.env.VITE_API_URL;

  async function criarNoticia() {
    if (!mensagem.trim()) {
      setStatus("Mensagem não pode estar vazia!");
      return;
    }
    setStatus("Enviando...");
    try {
      const res = await fetch(`${API_URL}/criar/noticias/admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ mensagem }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Erro ao criar notícia");
      }
      setMensagem("");
      setStatus("Notícia criada com sucesso!");
    } catch (err: any) {
      setStatus(`Erro: ${err.message}`);
    }
  }

  async function limparNoticias() {
    if (!window.confirm("Tem certeza que quer apagar todas as notícias? Isso não tem volta.")) return;

    setStatus("Limpando notícias...");
    try {
      const res = await fetch(`${API_URL}/noticias/limpar`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Erro ao limpar notícias");
      }
      setStatus("Todas as notícias foram apagadas e IDs resetados!");
    } catch (err: any) {
      setStatus(`Erro: ${err.message}`);
    }
  }

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden font-sans">
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      <section className="relative z-10 max-w-xl mx-auto p-8 space-y-6">
        <h1 className="text-3xl font-bold">📰 Painel de Notícias Newsmarquee</h1>

        <textarea
          rows={5}
          className="w-full text-black p-3 rounded-md border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Escreva a notícia aqui..."
          value={mensagem}
          onChange={(e) => setMensagem(e.target.value)}
        />

        <div className="flex gap-4">
          <button
            onClick={criarNoticia}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={status === "Enviando..."}
          >
            Criar Notícia
          </button>

          <button
            onClick={limparNoticias}
            className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded font-semibold transition"
          >
            Limpar Todas Notícias
          </button>
        </div>

        {status && (
          <p
            className={`mt-4 font-semibold ${
              status.startsWith("Erro") ? "text-red-500" : "text-green-400"
            }`}
          >
            {status}
          </p>
        )}
      </section>
    </main>
  );
}
