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

export function RankLista({ ranking }: RankListProps) {
  return (
    <div
      className="overflow-x-auto rounded-lg shadow-lg border border-gray-300"
      style={{
        position: "relative",
        zIndex: 3,
        backgroundColor: "rgba(240, 248, 255, 0.85)", // branco gelo translúcido
      }}
    >
      <table className="min-w-full border-separate border-spacing-y-1 text-gray-900">
        <thead>
          <tr className="text-left text-gray-600 text-xs uppercase tracking-wide select-none">
            <th className="px-2 py-1 sm:px-3 sm:py-2">Posição</th>
            <th className="px-2 py-1 sm:px-3 sm:py-2">Jogador</th>
            <th className="px-2 py-1 text-center font-mono sm:px-3 sm:py-2">Vitórias</th>
            <th className="px-2 py-1 text-center font-mono sm:px-3 sm:py-2">Rodadas</th>
            <th className="px-2 py-1 text-center font-mono sm:px-3 sm:py-2">Win %</th>
          </tr>
        </thead>
        <tbody>
          {ranking.map((jogador, index) => {
            let medalha = "";
            let medalhaClasses = "";
            if (index === 0) {
              medalha = "🥇";
              medalhaClasses = "text-blue-600 drop-shadow-[0_0_5px_rgba(59,130,246,0.9)]";
            } else if (index === 1) {
              medalha = "🥈";
              medalhaClasses = "text-blue-400 drop-shadow-[0_0_4px_rgba(147,197,253,0.8)]";
            } else if (index === 2) {
              medalha = "🥉";
              medalhaClasses = "text-blue-300 drop-shadow-[0_0_3px_rgba(191,219,254,0.7)]";
            } else {
              medalha = `#${index + 1}`;
              medalhaClasses = "text-gray-700";
            }

            return (
              <tr
                key={jogador.usuario_id}
                className="hover:bg-blue-100/50 transition-colors rounded-md cursor-default"
              >
                <td
                  className={`px-2 py-1 sm:px-3 sm:py-2 font-bold text-center whitespace-nowrap select-none ${medalhaClasses}`}
                  style={{ fontSize: "1rem" }}
                >
                  {medalha}
                </td>
                <td className="px-2 py-1 sm:px-3 sm:py-2 flex items-center gap-2">
                  <img
                    src={jogador.avatar_url || "/default-avatar.png"}
                    alt={jogador.nome}
                    className="w-6 h-6 sm:w-8 sm:h-8 rounded-full object-cover border border-blue-300 shadow-sm"
                    loading="lazy"
                  />
                  <div className="truncate">
                    <p className="font-semibold text-blue-900 tracking-tight leading-tight text-sm sm:text-base truncate">
                      {jogador.nome}
                    </p>
                    <p className="text-xs text-blue-700 select-text truncate">ID: {jogador.usuario_id}</p>
                  </div>
                </td>
                <td className="px-2 py-1 sm:px-3 sm:py-2 text-center font-mono whitespace-nowrap text-blue-700 font-semibold text-sm sm:text-base">
                  {jogador.vitorias}
                </td>
                <td className="px-2 py-1 sm:px-3 sm:py-2 text-center font-mono whitespace-nowrap text-blue-700 font-semibold text-sm sm:text-base">
                  {jogador.rodadas_jogadas}
                </td>
                <td className="px-2 py-1 sm:px-3 sm:py-2 text-center font-mono whitespace-nowrap text-blue-700 font-semibold text-sm sm:text-base">
                  {jogador.porcentagem_vitorias.toFixed(1)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
