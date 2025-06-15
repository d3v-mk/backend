import { useEffect, useState } from "react";
import { FormListarPromotores } from "@/PainelAdmin/components/FormListarPromotores";
import type { Promotor } from "@/types";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";

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

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Fundo animado */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo */}
      <div
        className="relative z-10 max-w-6xl mx-auto p-4 sm:p-8"
        style={{ fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif" }}
      >
        <h3 className="mb-4 text-2xl font-semibold">📋 Lista de Promotores</h3>

        <label className="block mb-6 font-semibold text-sm sm:text-base">
          Filtro Status:{" "}
          <select
            value={ativoFiltro}
            onChange={(e) => setAtivoFiltro(e.target.value as any)}
            className="ml-2 px-3 py-2 rounded bg-[#333366] text-white font-semibold cursor-pointer border-none focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="todos">Todos</option>
            <option value="ativos">Ativos</option>
            <option value="bloqueados">Bloqueados</option>
          </select>
        </label>

        {loading && <p className="italic text-gray-400">Carregando...</p>}
        {erro && <p className="text-red-500 font-bold">{erro}</p>}

        <div className="overflow-x-auto rounded-lg shadow-lg bg-zinc-800">
          <FormListarPromotores promotores={promotores} />
        </div>
      </div>
    </main>
  );
}
