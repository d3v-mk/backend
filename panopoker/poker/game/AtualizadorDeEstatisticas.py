from datetime import datetime
from typing import List, Tuple, Dict
from decimal import Decimal
from panopoker.usuarios.models.estatisticas import EstatisticasJogador
from panopoker.poker.models.mesa import JogadorNaMesa

class AtualizadorDeEstatisticas:
    @staticmethod
    def atualizar(
        jogadores_avaliados: List[Tuple[JogadorNaMesa, List[str], str]],
        vencedores_ids: List[int],
        valores_ganhos: Dict[int, Decimal],
        db
    ):
        for jogador, mao, rank in jogadores_avaliados:
            stats = db.query(EstatisticasJogador).filter_by(usuario_id=jogador.jogador_id).first()

            if not stats:
                stats = EstatisticasJogador(usuario_id=jogador.jogador_id)
                db.add(stats)

            stats.rodadas_jogadas = (stats.rodadas_jogadas or 0) + 1

            if jogador.jogador_id in vencedores_ids:
                stats.rodadas_ganhas = (stats.rodadas_ganhas or 0) + 1
                stats.vitorias = (stats.vitorias or 0) + 1

                ganho = valores_ganhos.get(jogador.jogador_id, Decimal("0.00"))
                
                fichas_atuais = stats.fichas_ganhas or Decimal("0.00")
                if not isinstance(fichas_atuais, Decimal):
                    fichas_atuais = Decimal(str(fichas_atuais))
                stats.fichas_ganhas = fichas_atuais + ganho

                # Atualiza maior pote
                maior_pote = stats.maior_pote or Decimal("0.00")
                if not isinstance(maior_pote, Decimal):
                    maior_pote = Decimal(str(maior_pote))
                stats.maior_pote = max(maior_pote, ganho)

                agora = datetime.utcnow()
                if not stats.data_primeira_vitoria:
                    stats.data_primeira_vitoria = agora
                stats.data_ultima_vitoria = agora

                mao_formatada = "-".join(sorted(mao))
                if not stats.mao_favorita:
                    stats.mao_favorita = mao_formatada
                elif stats.mao_favorita != mao_formatada:
                    pass
            else:
                perdidas = stats.fichas_perdidas or Decimal("0.00")
                if not isinstance(perdidas, Decimal):
                    perdidas = Decimal(str(perdidas))
                aposta = jogador.aposta_atual or Decimal("0.00")
                if not isinstance(aposta, Decimal):
                    aposta = Decimal(str(aposta))
                stats.fichas_perdidas = perdidas + aposta

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
