import { useRank } from "../hooks/useRank";
import { RankLayout } from "../layout/RankLayout";
import { RankLista } from "../components/RankLista";

export default function RankPage() {
  const { ranking, loading, error } = useRank(10, 0);

  return (
    <RankLayout>
      <div>
        {loading ? (
          <p className="text-center text-lg text-gray-300">Carregando ranking...</p>
        ) : error ? (
          <p className="text-center text-lg text-red-500">Erro: {error}</p>
        ) : (
          <RankLista ranking={ranking} />
        )}
      </div>
    </RankLayout>
  );
}
