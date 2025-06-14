import { useState } from "react";

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
        credentials: "include", // ⚠️ envia cookie automaticamente
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
        credentials: "include", // ⚠️ envia cookie automaticamente
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
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Painel de Notícias Newsmarquee</h1>

      <textarea
        rows={4}
        className="w-full text-black p-2 border rounded mb-2"
        placeholder="Escreva a notícia aqui..."
        value={mensagem}
        onChange={(e) => setMensagem(e.target.value)}
      />

      <button
        onClick={criarNoticia}
        className="bg-blue-600 text-white px-4 py-2 rounded mr-4 hover:bg-blue-700"
      >
        Criar Notícia
      </button>

      <button
        onClick={limparNoticias}
        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Limpar Todas Notícias
      </button>

      {status && <p className="mt-4 text-black dark:text-gray-200">{status}</p>}
    </div>
  );
}
