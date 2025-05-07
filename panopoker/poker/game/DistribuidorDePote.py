from sqlalchemy.orm import Session
from app.core.debug import debug_print
from app.models.mesa import Mesa, JogadorNaMesa
from app.game.poker.avaliar_maos import avaliar_mao
import json
import time
from threading import Thread
from typing import List, Tuple

class DistribuidorDePote:
    def __init__(self, mesa: Mesa, db: Session):
        self.db = db
        self.mesa = db.merge(mesa)

    def _resetador(self):
        from app.game.poker.ResetadorDePartida import ResetadorDePartida
        return ResetadorDePartida(self.mesa, self.db)

    def realizar_showdown(self):
        debug_print(f"[SHOWDOWN] Iniciando showdown na mesa {self.mesa.id}")

        # Atualiza o pote total a partir das apostas acumuladas
        self.atualizar_pote_total()

        # Marca a fase como showdown e persiste
        self.mesa.estado_da_rodada = "showdown"
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"[SHOWDOWN] Estado definido como 'showdown' e commit realizado")

        # Extrai cartas comunitárias
        comunitarias = (
            self.mesa.cartas_comunitarias
            if isinstance(self.mesa.cartas_comunitarias, dict)
            else json.loads(self.mesa.cartas_comunitarias)
        )
        cartas_mesa = []
        cartas_mesa.extend(comunitarias.get("flop", []))
        if comunitarias.get("turn"): cartas_mesa.append(comunitarias["turn"])
        if comunitarias.get("river"): cartas_mesa.append(comunitarias["river"])
        debug_print(f"[SHOWDOWN] Cartas da mesa: {cartas_mesa}")

        # Identifica participantes ativos (não foldados)
        participantes = [
            j for j in self.db.query(JogadorNaMesa)
                    .filter(JogadorNaMesa.mesa_id == self.mesa.id)
                    .all()
            if j.participando_da_rodada and not j.foldado
        ]

        # Distribui o pote total igualmente entre os vencedores (ignora side pots por aposta_atual)
        side_pots = [(self.mesa.pote_total, participantes)]
        vencedores_ids = []
        for amount, grupo in side_pots:
            # Avalia cada mão e determina o melhor rank
            resultados = [(j, avaliar_mao(cartas_mesa + (json.loads(j.cartas) if j.cartas else []))) for j in grupo]
            best_rank = max(r for _, r in resultados)
            winners = [j for j, r in resultados if r == best_rank]
            ganho = amount / len(winners) if winners else 0
            vencedores_ids.extend([j.jogador_id for j in winners])
            for w in winners:
                w.saldo_atual += ganho
                self.db.add(w)
            debug_print(f"[SHOWDOWN] Pote {amount:.2f} distribuído a {[w.jogador_id for w in winners]} cada {ganho:.2f}")

        # Zera o pote e commita
        self.mesa.pote_total = 0.0
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"[SHOWDOWN] Pote zerado após distribuição e commit realizado")

        # Prepara payload de retorno
        payload = {
            "mesa_id": self.mesa.id,
            "showdown": [
                {"jogador_id": j.jogador_id,
                 "cartas": (json.loads(j.cartas) if j.cartas else []),
                 "rank": avaliar_mao(cartas_mesa + (json.loads(j.cartas) if j.cartas else [])),
                 "foldado": j.foldado
                } for j in self.db.query(JogadorNaMesa).filter(JogadorNaMesa.mesa_id == self.mesa.id).all()
            ],
            "vencedores": list(set(vencedores_ids))
        }

        # Agenda nova rodada em background
        def delayed_reset():
            time.sleep(5)
            debug_print(f"[SHOWDOWN] Executando nova_rodada após delay de 5s")
            self._resetador().nova_rodada()
        Thread(target=delayed_reset, daemon=True).start()
        debug_print("[SHOWDOWN] nova_rodada agendada em background (5s)")

        return payload

    def _calcular_side_pots(self, jogadores: List[JogadorNaMesa]) -> List[Tuple[float, List[JogadorNaMesa]]]:
        """
        Calcula side pots a partir das apostas de cada jogador.
        Retorna lista de tuplas (valor_do_pote, lista_de_jogadores_eligiveis).
        """
        # ordena por aposta
        bets = sorted([(j, j.aposta_atual) for j in jogadores], key=lambda x: x[1])
        side_pots: List[Tuple[float, List[JogadorNaMesa]]] = []
        prev_amount = 0.0
        remaining = bets.copy()
        while remaining:
            _, amount = remaining[0]
            delta = amount - prev_amount
            contributors = [j for j, _ in remaining]
            pot = delta * len(contributors)
            side_pots.append((pot, contributors.copy()))
            prev_amount = amount
            # remove quem contribuiu exatamente esse nível
            remaining = [(j, a) for j, a in remaining if a > amount]
        return side_pots

    def _identificar_vencedores(self, resultados: List[Tuple[JogadorNaMesa, int]]) -> List[JogadorNaMesa]:
        """
        Dada lista (jogador, rank), retorna quem tem o menor rank.
        """
        resultados.sort(key=lambda x: x[1], reverse=True)
        melhor_rank = resultados[0][1]
        return [j for j, r in resultados if r == melhor_rank]

    def atualizar_pote_total(self):
        debug_print(f"[ATUALIZAR_POTE_TOTAL] Atualizando pote na mesa {self.mesa.id}")
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )

        # Soma todas as apostas atuais (rodada final) e adiciona ao pote
        total = sum(j.aposta_atual for j in jogadores)
        self.mesa.pote_total += total
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"[ATUALIZAR_POTE_TOTAL] Adicionado R${total:.2f} ao pote. Total agora R${self.mesa.pote_total:.2f}")

    def distribuir_pote(self, vencedor: JogadorNaMesa):
        # ✅ FORÇA RECARREGAR A MESA DO BANCO (pegando valor certo do pote atualizado no commit anterior)
        vencedor = self.db.merge(vencedor)
        self.db.refresh(self.mesa)

        # Se ainda não houve avanço de fase (ex: fold pré-flop), coletar blinds
        if self.mesa.estado_da_rodada == "pre-flop" and self.mesa.pote_total == 0:
            jogadores = (
                self.db.query(JogadorNaMesa)
                .filter(JogadorNaMesa.mesa_id == self.mesa.id)
                .all()
            )
            valor_pote = sum(j.aposta_atual for j in jogadores if j.aposta_atual)
            self.mesa.pote_total = round(valor_pote, 2)
            debug_print(f"[DISTRIBUIR_POTE] Coletando blinds direto: R${self.mesa.pote_total:.2f}")

        valor = self.mesa.pote_total
        debug_print(f"[DISTRIBUIR_POTE] Entregando R${valor:.2f} para jogador {vencedor.jogador_id}")

        vencedor.saldo_atual += valor
        self.db.add(vencedor)

        self.mesa.pote_total = 0.0
        self.db.add(self.mesa)
        self.db.commit()

        debug_print(f"[SHOWDOWN] Pote R${valor:.2f} distribuído a [{vencedor.jogador_id}] cada R${valor:.2f}")
        debug_print("[DISTRIBUIR_POTE] Pote zerado após distribuição")



