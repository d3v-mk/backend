import { useState } from "react";
import type { FormEvent } from "react";


export default function GerenciarCargo() {
  const [acaoSelecionada, setAcaoSelecionada] = useState<"promover" | "despromover">("promover");
  const [formPromoverUserId, setFormPromoverUserId] = useState<number | "">("");

  async function handlePromoverSubmit(e: FormEvent) {
    e.preventDefault();
    if (!formPromoverUserId) {
      alert("Informe o ID do usuário");
      return;
    }
    
    const API_URL = import.meta.env.VITE_API_URL;

    try {
      const res = await fetch(`${API_URL}/admin/usuario/${acaoSelecionada}/${formPromoverUserId}?tipo=promotor`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        const errorMsg = errData?.detail || errData?.msg || "Erro desconhecido";
        alert("❌ " + errorMsg);
        return;
      }

      const data = await res.json();
      alert("✅ " + (data.msg || "Operação concluída com sucesso!"));
      setFormPromoverUserId(""); // limpa input após sucesso
    } catch (error: any) {
      alert("❌ Erro na requisição: " + (error.message || "desconhecido"));
    }
  }

  return (
    <section className="bg-gray-800 p-6 rounded-lg shadow-md max-w-lg mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Gerenciar Cargo de Promotor</h2>
      <form onSubmit={handlePromoverSubmit} className="space-y-4">
        <label className="block font-medium text-gray-300">🆔 ID do Usuário:</label>
        <input
          type="number"
          value={formPromoverUserId}
          onChange={(e) => setFormPromoverUserId(e.target.value === "" ? "" : Number(e.target.value))}
          placeholder="Ex: 42"
          required
          className="w-full px-3 py-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="flex justify-center gap-4">
          <button
            type="submit"
            onClick={() => setAcaoSelecionada("promover")}
            className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2 rounded transition"
          >
            ✅ Promover
          </button>
          <button
            type="submit"
            onClick={() => setAcaoSelecionada("despromover")}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-2 rounded transition"
          >
            ❌ Remover
          </button>
        </div>
      </form>
    </section>
  );
}
