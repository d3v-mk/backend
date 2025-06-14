import { useEffect, useState } from "react";
import { FormListarPromotores } from "@/PainelAdmin/components/FormListarPromotores";
import type { Promotor } from "@/types";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect"; // Ajusta caminho se precisar

export default function PageListarPromotores() {
  const [promotores, setPromotores] = useState<Promotor[]>([]);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");
  const [ativoFiltro, setAtivoFiltro] = useState<"todos" | "ativos" | "bloqueados">("todos");
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    listarPromotores();
  }, [ativoFiltro]);

  async function listarPromotores() {
    setLoading(true);
    setErro("");
    try {
      const res = await fetch(`${API_URL}/admin/promotor/listar?ativo=${ativoFiltro}`, {
        method: "GET",
        credentials: "include",
      });

      if (!res.ok) throw new Error("Falha ao buscar promotores");
      const data = await res.json();
      setPromotores(data);
    } catch (err: any) {
      setErro(err.message || "Erro desconhecido");
    }
    setLoading(false);
  }

  const copiarId = (id: number) => {
    navigator.clipboard.writeText(id.toString());
    alert("ID copiado: " + id);
  };

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Fundo animado */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo */}
      <div
        className="relative z-10 max-w-4xl mx-auto p-8"
        style={{ fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif" }}
      >
        <h3 className="mb-3 text-xl font-semibold">📋 Lista de Promotores</h3>

        <label className="block mb-4 font-semibold">
          Filtro Status:{" "}
          <select
            value={ativoFiltro}
            onChange={(e) => setAtivoFiltro(e.target.value as any)}
            className="ml-2 px-3 py-1 rounded bg-[#333366] text-white font-semibold cursor-pointer border-none"
          >
            <option value="todos">Todos</option>
            <option value="ativos">Ativos</option>
            <option value="bloqueados">Bloqueados</option>
          </select>
        </label>

        {loading && <p className="italic text-gray-400">Carregando...</p>}
        {erro && <p className="text-red-500 font-bold">{erro}</p>}

        <FormListarPromotores promotores={promotores} onCopiarId={copiarId} />
      </div>
    </main>
  );
}
