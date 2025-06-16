import { useState, useMemo } from "react";

type Jogador = {
  usuario_id: number;
  nome: string;
  avatar_url?: string | null;
  vitorias: number;
  rodadas_jogadas: number;
  porcentagem_vitorias: number;
};

type RankListProps = {
  ranking: Jogador[];
};

type OrderBy = "vitorias" | "rodadas" | "winrate";

export function RankLista({ ranking }: RankListProps) {
  const [orderBy, setOrderBy] = useState<OrderBy>("vitorias");

  const rankingOrdenado = useMemo(() => {
    return [...ranking].sort((a, b) => {
      if (orderBy === "vitorias") return b.vitorias - a.vitorias;
      if (orderBy === "rodadas") return b.rodadas_jogadas - a.rodadas_jogadas;
      return b.porcentagem_vitorias - a.porcentagem_vitorias;
    });
  }, [ranking, orderBy]);

  return (
    <div className="relative text-white z-10">
      <div className="mb-6 flex justify-center">
        <select
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value as OrderBy)}
          className="bg-gray-800 text-white border border-gray-600 rounded-md px-3 py-2 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 transition"
        >
          <option value="vitorias">+ Vitórias</option>
          <option value="rodadas">+ Rodadas</option>
          <option value="winrate">Maior Win %</option>
        </select>
      </div>

      {/* Tabela desktop */}
      <div className="hidden sm:block overflow-x-auto border border-gray-700 rounded-lg shadow-lg">
        <table className="min-w-full border-separate border-spacing-y-1">
          <thead className="bg-gray-800">
            <tr className="text-gray-400 text-sm uppercase">
              <th className="px-4 py-2 text-left">Posição</th>
              <th className="px-4 py-2 text-left">Jogador</th>
              <th className="px-4 py-2 text-center">Vitórias</th>
              <th className="px-4 py-2 text-center">Rodadas</th>
              <th className="px-4 py-2 text-center">Win %</th>
            </tr>
          </thead>
          <tbody>
            {rankingOrdenado.map((jogador, index) => {
              const medalha =
                index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `#${index + 1}`;
              return (
                <tr
                  key={jogador.usuario_id}
                  className="bg-gray-900 hover:bg-gray-800 transition rounded-md"
                >
                  <td className="px-4 py-3 font-bold text-center">{medalha}</td>
                  <td className="px-4 py-3 flex items-center gap-3">
                    <img
                      src={jogador.avatar_url || "/default-avatar.png"}
                      alt={jogador.nome}
                      className="w-9 h-9 rounded-full border border-gray-600 object-cover"
                    />
                    <div>
                      <p className="font-semibold text-sm truncate">{jogador.nome}</p>
                      <p className="text-xs text-gray-400">ID: {jogador.usuario_id}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-blue-400">
                    {jogador.vitorias}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-blue-300">
                    {jogador.rodadas_jogadas}
                  </td>
                  <td className="px-4 py-3 text-center font-mono text-green-400">
                    {jogador.porcentagem_vitorias.toFixed(1)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Cards mobile */}
      <div className="block sm:hidden space-y-2">
        {rankingOrdenado.map((jogador, index) => {
          const medalha =
            index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : `#${index + 1}`;
          return (
            <div
              key={jogador.usuario_id}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 flex gap-3 items-center shadow-md"
            >
              <div className="text-xl font-bold">{medalha}</div>
              <img
                src={jogador.avatar_url || "/default-avatar.png"}
                alt={jogador.nome}
                className="w-10 h-10 rounded-full object-cover border border-gray-600"
              />
              <div className="flex-1">
                <div className="text-sm font-semibold truncate">{jogador.nome}</div>
                <div className="text-xs text-gray-400">ID: {jogador.usuario_id}</div>
                <div className="text-xs mt-1 text-blue-300 font-mono">
                  🏆 {jogador.vitorias} vitórias • 🎮 {jogador.rodadas_jogadas} rodadas
                </div>
                <div className="text-xs text-green-400 font-mono">
                  Win Rate: {jogador.porcentagem_vitorias.toFixed(1)}%
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
