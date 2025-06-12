import { FormCriarPromotor } from "../components/FormCriarPromotor";
import { useState } from "react";

export default function CriarPromotorPage() {
  const [resultadoCriar, setResultadoCriar] = useState("");

  async function criarPromotor(data: any) {
    const res = await fetch("/admin/promotor/criar_loja", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...data,
        user_id: Number(data.user_id),
        nome: data.nome || null,
      }),
    });

    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || "Erro desconhecido");
    setResultadoCriar(result.msg);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">➕ Criar Loja do Promotor</h1>
      <FormCriarPromotor
        onCriar={criarPromotor}
        resultadoCriar={resultadoCriar}
        setResultadoCriar={setResultadoCriar}
      />
    </div>
  );
}
