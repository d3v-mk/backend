// src/pages/promotor/VerSaquesPage.tsx
import { useEffect, useState } from "react";
import { FaCheckCircle, FaTimesCircle, FaClock } from "react-icons/fa";

type Jogador = {
  id: number;
  nome: string;
  id_publico: string;
};

type Saque = {
  id: number;
  valor: string;
  status: string;
  criado_em: string | null;
  jogador: Jogador;
};

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    aguardando: "bg-yellow-100 text-yellow-800",
    aprovado: "bg-green-100 text-green-800",
    rejeitado: "bg-red-100 text-red-800",
    pago: "bg-blue-100 text-blue-800",
  };
  return colors[status.toLowerCase()] || "bg-gray-100 text-gray-700";
}

function statusIcon(status: string) {
  switch (status.toLowerCase()) {
    case "aprovado":
      return <FaCheckCircle className="text-green-600 inline mr-1" />;
    case "rejeitado":
      return <FaTimesCircle className="text-red-600 inline mr-1" />;
    case "aguardando":
      return <FaClock className="text-yellow-600 inline mr-1" />;
    case "pago":
      return <FaCheckCircle className="text-blue-600 inline mr-1" />;
    default:
      return null;
  }
}

export default function VerSaquesPage() {
  const [saques, setSaques] = useState<Saque[]>([]);
  const [carregando, setCarregando] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchSaques = async () => {
      try {
        const resp = await fetch(`${API_URL}/promotor/saques`, {
          credentials: "include",
        });
        const data = await resp.json();
        setSaques(data.saques || []);
      } catch (err) {
        console.error("Erro ao buscar saques:", err);
      } finally {
        setCarregando(false);
      }
    };

    fetchSaques();
  }, []);

  if (carregando) {
    return <div className="p-4">Carregando saques...</div>;
  }

  if (saques.length === 0) {
    return <div className="p-4 text-gray-600">Nenhum saque encontrado.</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">📄 Lista de Saques</h1>
      <div className="overflow-x-auto max-h-[450px] overflow-y-auto border rounded shadow-md">
        <table className="min-w-full border-collapse border border-gray-300">
          <thead className="bg-gray-100 sticky top-0 z-10">
            <tr>
              <th className="py-2 px-4 border-b cursor-pointer select-none hover:bg-gray-200">
                Jogador ⬆️⬇️
              </th>
              <th className="py-2 px-4 border-b">ID Público</th>
              <th className="py-2 px-4 border-b">Valor</th>
              <th className="py-2 px-4 border-b">Status</th>
              <th className="py-2 px-4 border-b">Data</th>
            </tr>
          </thead>
          <tbody>
            {saques.map((saque) => (
              <tr
                key={saque.id}
                className="hover:bg-blue-50 transition-colors duration-200 cursor-pointer"
                tabIndex={0}
                onClick={() =>
                  alert(`Saque #${saque.id} do jogador ${saque.jogador.nome}`)
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") alert(`Saque #${saque.id}`);
                }}
              >
                <td className="py-2 px-4 border-b">{saque.jogador.nome}</td>
                <td className="py-2 px-4 border-b">{saque.jogador.id_publico}</td>
                <td className="py-2 px-4 border-b">
                  {Number(saque.valor).toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  })}
                </td>
                <td className="py-2 px-4 border-b flex items-center">
                  {statusIcon(saque.status)}
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-semibold ${statusBadge(
                      saque.status
                    )}`}
                  >
                    {saque.status.charAt(0).toUpperCase() + saque.status.slice(1)}
                  </span>
                </td>
                <td className="py-2 px-4 border-b">
                  {saque.criado_em
                    ? new Date(saque.criado_em).toLocaleString("pt-BR")
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
