import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";
import { BackgroundPokerEffect } from "@/home/components/BackgroundPokerEffect";

type SaldoResponse = {
  saldo_repassar: number;
  comissao_total: number;
  bloqueado: boolean;
};

export default function DashBoardPage() {
  const [saldo, setSaldo] = useState<SaldoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    fetch(`${API_URL}/promotor/info`, {
      method: "GET",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Falha ao carregar saldo");
        return res.json();
      })
      .then((data: SaldoResponse) => setSaldo(data))
      .catch((err) => console.error("Erro ao buscar saldo:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-white">Carregando saldo...</p>;
  if (!saldo) return <p className="text-red-400">Não foi possível carregar os dados.</p>;

  return (
    <main className="relative min-h-screen bg-gray-950 text-white overflow-hidden">
      {/* Fundo animado com z-index: 1 */}
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
        <BackgroundPokerEffect />
      </div>

      {/* Conteúdo acima do efeito */}
      <div className="relative z-10 p-6 max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-6">Dashboard do Promotor</h1>

        {/* Status de bloqueio centralizado */}
        <div
          className={`mb-6 flex items-center justify-center space-x-2 font-semibold px-4 py-2 rounded-xl
            ${
              saldo.bloqueado
                ? "bg-red-700 text-red-100 border border-red-400"
                : "bg-green-700 text-green-100 border border-green-400"
            }
          `}
        >
          {saldo.bloqueado ? (
            <>
              <AlertCircle className="w-6 h-6" />
              <span>🚫 Bloqueado: Entre em contato com suporte</span>
            </>
          ) : (
            <>
              <CheckCircle className="w-6 h-6" />
              <span>✅ Liberado para operar</span>
            </>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Caixa 1: Saldo a Repassar */}
          <div className="bg-gray-900 p-6 rounded-2xl shadow-inner flex items-center space-x-4 border border-gray-700">
            <div className="bg-gray-800 p-3 rounded-full">
              <DollarSign className="text-green-400 w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Saldo a Repassar</p>
              <p className="text-2xl font-mono font-bold text-white">
                R$ {saldo.saldo_repassar.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Caixa 2: Comissão Total */}
          <div className="bg-gray-900 p-6 rounded-2xl shadow-inner flex items-center space-x-4 border border-gray-700">
            <div className="bg-gray-800 p-3 rounded-full">
              <TrendingUp className="text-yellow-400 w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-gray-400">Comissão Total</p>
              <p className="text-2xl font-mono font-bold text-white">
                R$ {saldo.comissao_total.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
