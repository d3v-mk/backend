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

            # Aumenta contagem de rodadas jogadas
            stats.rodadas_jogadas += 1

            # Se venceu a mão
            if jogador.jogador_id in vencedores_ids:
                stats.rodadas_ganhas += 1
                stats.vitorias += 1
                ganho = valores_ganhos.get(jogador.jogador_id, 0.0)
                stats.fichas_ganhas += ganho

                # Atualiza maior pote
                if ganho > stats.maior_pote:
                    stats.maior_pote = ganho

                # Atualiza datas de vitória
                agora = datetime.utcnow()
                if not stats.data_primeira_vitoria:
                    stats.data_primeira_vitoria = agora
                stats.data_ultima_vitoria = agora

                # Mão favorita (mais recorrente nas vitórias)
                mao_formatada = "-".join(sorted(mao))
                if stats.mao_favorita == mao_formatada:
                    pass  # já tá
                elif not stats.mao_favorita:
                    stats.mao_favorita = mao_formatada
                else:
                    # aqui você poderia fazer algo mais complexo depois (ex: contagem)
                    pass

            else:
                stats.fichas_perdidas += jogador.aposta_atual

            # Tipo de mão vencida
            match rank:
                case "straight": stats.sequencias += 1
                case "flush": stats.flushes += 1
                case "full_house": stats.fullhouses += 1
                case "four_of_a_kind": stats.quadras += 1
                case "straight_flush": stats.straight_flushes += 1
                case "royal_flush": stats.royal_flushes += 1

            # Último update
            stats.ultimo_update = datetime.utcnow()

        db.commit()
