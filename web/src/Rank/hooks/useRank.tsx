import { useState, useEffect } from "react";

export type Jogador = {
  usuario_id: number;
  nome: string;
  avatar_url: string | null;
  vitorias: number;
  rodadas_jogadas: number;
  porcentagem_vitorias: number;
};

export function useRank(limit = 10, offset = 0) {
  const [ranking, setRanking] = useState<Jogador[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRanking = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/ranking/geral?limit=${limit}&offset=${offset}`);
        if (!response.ok) throw new Error("Erro ao buscar o ranking");
        const data = await response.json();
        setRanking(data.ranking);
      } catch (err) {
        setError((err as Error).message || "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    };

    fetchRanking();
  }, [limit, offset]);

  return { ranking, loading, error };
}
