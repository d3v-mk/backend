// src/pages/promotor/SacarPage.tsx
import { useState } from "react";

export default function SacarPage() {
  const [idJogador, setIdJogador] = useState("");
  const [valor, setValor] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [mensagem, setMensagem] = useState("");

  const API_URL = import.meta.env.VITE_API_URL;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    <div className="max-w-xl mx-auto mt-10 bg-white p-6 rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-4">📤 Solicitar Saque</h1>

      {mensagem && (
        <div className="mb-4 p-3 bg-blue-100 text-blue-700 rounded">
          {mensagem}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="idJogador" className="block font-medium text-gray-700">
            ID Público do Jogador
          </label>
          <input
            type="text"
            id="idJogador"
            value={idJogador}
            onChange={(e) => setIdJogador(e.target.value)}
            required
            className="w-full border px-3 py-2 rounded-md focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>

        <div>
          <label htmlFor="valor" className="block font-medium text-gray-700">
            Valor do Saque (ex: 10.00)
          </label>
          <input
            type="number"
            step="0.01"
            id="valor"
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            required
            className="w-full border px-3 py-2 rounded-md focus:outline-none focus:ring focus:border-blue-300"
          />
        </div>

        <button
          type="submit"
          disabled={enviando}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {enviando ? "Enviando..." : "Solicitar Saque"}
        </button>
      </form>
    </div>
  );
}
