from datetime import datetime
from typing import List, Tuple, Dict
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
from panopoker.poker.models.mesa import JogadorNaMesa

class AtualizadorDeEstatisticas:
    @staticmethod
    def atualizar(
        jogadores_avaliados: List[Tuple[JogadorNaMesa, List[str], str]],
        vencedores_ids: List[int],
        valores_ganhos: Dict[int, float],
        db
    ):
        for jogador, mao, rank in jogadores_avaliados:
            stats = db.query(EstatisticasJogador).filter_by(usuario_id=jogador.jogador_id).first()

            if not stats:
                stats = EstatisticasJogador(usuario_id=jogador.jogador_id)
                db.add(stats)

            # Proteção contra None nos campos numéricos
            stats.rodadas_jogadas = (stats.rodadas_jogadas or 0) + 1

            if jogador.jogador_id in vencedores_ids:
                stats.rodadas_ganhas = (stats.rodadas_ganhas or 0) + 1
                stats.vitorias = (stats.vitorias or 0) + 1

                ganho = valores_ganhos.get(jogador.jogador_id, 0.0)
                stats.fichas_ganhas = (stats.fichas_ganhas or 0.0) + ganho

                # Atualiza maior pote
                stats.maior_pote = max(stats.maior_pote or 0.0, ganho)

                agora = datetime.utcnow()
                if not stats.data_primeira_vitoria:
                    stats.data_primeira_vitoria = agora
                stats.data_ultima_vitoria = agora

                mao_formatada = "-".join(sorted(mao))
                if not stats.mao_favorita:
                    stats.mao_favorita = mao_formatada
                elif stats.mao_favorita != mao_formatada:
                    pass  # pode implementar contagem no futuro
            else:
                stats.fichas_perdidas = (stats.fichas_perdidas or 0.0) + (jogador.aposta_atual or 0.0)

            # Tipo de mão vencida
            match rank:
                case "straight":
                    stats.sequencias = (stats.sequencias or 0) + 1
                case "flush":
                    stats.flushes = (stats.flushes or 0) + 1
                case "full_house":
                    stats.fullhouses = (stats.fullhouses or 0) + 1
                case "four_of_a_kind":
                    stats.quadras = (stats.quadras or 0) + 1
                case "straight_flush":
                    stats.straight_flushes = (stats.straight_flushes or 0) + 1
                case "royal_flush":
                    stats.royal_flushes = (stats.royal_flushes or 0) + 1

            stats.ultimo_update = datetime.utcnow()

        db.commit()
