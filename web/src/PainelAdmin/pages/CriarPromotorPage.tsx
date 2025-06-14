import { useState } from "react";
import { FormCriarPromotor } from "../components/FormCriarPromotor";
import type { FormData } from "../components/FormCriarPromotor";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect"; // ajusta o path se precisar

export default function CriarPromotorPage() {
  const [resultadoCriar, setResultadoCriar] = useState("");

  async function criarLoja(data: FormData) {
    setResultadoCriar("");

    const API_URL = import.meta.env.VITE_API_URL;

    try {
      const res = await fetch(`${API_URL}/admin/promotor/criar_loja`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...data,
          user_id: Number(data.user_id),
          nome: data.nome || null,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        const errorMsg = errData?.detail || errData?.msg || "Erro desconhecido";
        throw new Error(errorMsg);
      }

      const result = await res.json();
      setResultadoCriar(result.msg || "Loja criada com sucesso!");
    } catch (error: any) {
      setResultadoCriar("❌ " + (error.message || "Erro ao criar loja"));
    }
  }

  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Fundo animado */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">➕ Criar Loja do Promotor</h1>
        <FormCriarPromotor onCriar={criarLoja} resultadoCriar={resultadoCriar} />
      </div>
    </main>
  );
}
