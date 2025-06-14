import { useState } from "react";
//import { useAuth } from "../../hooks/useAuth";

export default function ManutencaoPage() {
  //const { user } = useAuth(); // se precisar info do usuário/admin
  const [loading, setLoading] = useState(false);
  const [mensagem, setMensagem] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL;

  async function ativarManutencao() {
    setLoading(true);
    setMensagem(null);
    setErro(null);
    try {
      const res = await fetch(`${API_URL}/admin/ativar-manutencao`, {
        method: "POST",
        credentials: "include", // manda cookie pra manter auth
      });
      if (!res.ok) throw new Error("Falha ao ativar manutenção");
      const data = await res.json();
      setMensagem(data.msg);
    } catch (err: any) {
      setErro(err.message || "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  async function encerrarManutencao() {
    setLoading(true);
    setMensagem(null);
    setErro(null);
    try {
      const res = await fetch(`${API_URL}/admin/encerrar-manutencao`, {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) throw new Error("Falha ao encerrar manutenção");
      const data = await res.json();
      setMensagem(data.msg + (data.mesas_reabertas ? ` (Mesas reabertas: ${data.mesas_reabertas.join(", ")})` : ""));
    } catch (err: any) {
      setErro(err.message || "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20, color: "#eee", fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif" }}>
      <h2>⚙️ Painel de Manutenção</h2>
      <p>Ative a manutenção para mesas em jogo e abertas, ou encerre a manutenção para reabrir mesas.</p>

      <button
        onClick={ativarManutencao}
        disabled={loading}
        style={{
          marginRight: 10,
          padding: "10px 20px",
          backgroundColor: "#c0392b",
          border: "none",
          borderRadius: 6,
          color: "white",
          cursor: "pointer",
        }}
      >
        {loading ? "Processando..." : "Ativar Manutenção"}
      </button>

      <button
        onClick={encerrarManutencao}
        disabled={loading}
        style={{
          padding: "10px 20px",
          backgroundColor: "#27ae60",
          border: "none",
          borderRadius: 6,
          color: "white",
          cursor: "pointer",
        }}
      >
        {loading ? "Processando..." : "Encerrar Manutenção"}
      </button>

      {mensagem && <p style={{ marginTop: 20, color: "#2ecc71", fontWeight: "600" }}>{mensagem}</p>}
      {erro && <p style={{ marginTop: 20, color: "#e74c3c", fontWeight: "600" }}>{erro}</p>}
    </div>
  );
}
