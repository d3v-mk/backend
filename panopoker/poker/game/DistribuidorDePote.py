from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
import json
import time
from threading import Thread
from typing import List, Tuple
from panopoker.poker.game.avaliar_maos import avaliar_mao
from panopoker.websocket.manager import connection_manager
import asyncio

class DistribuidorDePote:
    def __init__(self, mesa: Mesa, db: Session):
        self.db = db
        self.mesa = mesa

    def _resetador(self):
        from panopoker.poker.game.ResetadorDePartida import ResetadorDePartida
        return ResetadorDePartida(self.mesa, self.db)



    async def realizar_showdown(self):
        from panopoker.poker.game.utils.estatisticas_helper import registrar_estatisticas_showdown
        from panopoker.poker.game.utils.wincards_helper import wincards_helper

        debug_print(f"[SHOWDOWN] Iniciando showdown na mesa {self.mesa.id}")

        # Garante que o pote está correto
        if self.mesa.pote_total == 0:
            self.atualizar_pote_total()

        self.mesa.estado_da_rodada = "showdown"
        self.db.add(self.mesa)
        self.db.commit()

        # Pega as cartas comunitárias da mesa
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

        # Só jogadores que estão participando da rodada e não deram fold
        participantes = [
            j for j in self.db.query(JogadorNaMesa)
                    .filter(JogadorNaMesa.mesa_id == self.mesa.id)
                    .all()
            if j.participando_da_rodada and not j.foldado
        ]

        # Mostra info das mãos de cada participante no log
        for j in participantes:
            hole_cards = json.loads(j.cartas) if isinstance(j.cartas, str) else j.cartas
            rank = avaliar_mao(hole_cards + cartas_mesa)
            debug_print(f"[SHOWDOWN] Jogador {j.jogador_id} cartas: {hole_cards} – rank: {rank}")

        # Calcula side pots e distribui
        side_pots = self._calcular_side_pots(participantes)
        vencedores_ids = []
        for amount, grupo in side_pots:
            resultados = []
            for j in grupo:
                hole = json.loads(j.cartas) if isinstance(j.cartas, str) else j.cartas
                resultados.append((j, avaliar_mao(hole + cartas_mesa)))
            winners = self._identificar_vencedores(resultados)
            ganho = amount / len(winners) if winners else 0
            vencedores_ids.extend([j.jogador_id for j in winners])
            for w in winners:
                w.saldo_atual += ganho
                self.db.add(w)
            debug_print(f"[SHOWDOWN] Pote {amount:.2f} distribuído a {[w.jogador_id for w in winners]} cada {ganho:.2f}")

        self.mesa.pote_total = 0.0
        self.db.add(self.mesa)
        self.db.commit()

        # Todos os jogadores da mesa (para mostrar showdown até dos foldados)
        jogadores_na_mesa = self.db.query(JogadorNaMesa).filter(
            JogadorNaMesa.mesa_id == self.mesa.id
        ).all()

        # 🚨 Helper novo: retorna showdown detalhado pra cada jogador!
        showdown_payload = wincards_helper(
            jogadores=jogadores_na_mesa,
            cartas_mesa=cartas_mesa,
            vencedores_ids=set(vencedores_ids)
        )

        payload = {
            "mesa_id": self.mesa.id,
            "showdown": showdown_payload,
            "vencedores": list(set(vencedores_ids))
        }

        # (Opcional) Delay de 5s pra nova rodada
        async def reset_com_delay():
            await asyncio.sleep(5)
            debug_print(f"[SHOWDOWN] Executando nova_rodada após delay de 5s")
            await self._resetador().nova_rodada()

        asyncio.create_task(reset_com_delay())

        # Registrar estatísticas (se precisar)
        registrar_estatisticas_showdown(
            participantes=participantes,
            payload_showdown=payload["showdown"],
            side_pots=side_pots,
            db=self.db
        )

        # Broadcast via WebSocket
        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "showdown",
            "dados": payload
        })

        return payload
    






    
    def _calcular_side_pots(self, jogadores: List[JogadorNaMesa]) -> List[Tuple[float, List[JogadorNaMesa]]]:
        # ordena por aposta
        bets = sorted([(j, j.aposta_acumulada) for j in jogadores], key=lambda x: x[1])
        side_pots: List[Tuple[float, List[JogadorNaMesa]]] = []
        prev_amount = 0.0
        remaining = bets.copy()

        while remaining:
            _, amount = remaining[0]
            delta = amount - prev_amount
            contributors = [j for j, _ in remaining]
            pot = delta * len(contributors)
            side_pots.append((pot, contributors.copy()))
            debug_print(f"📦 Side pot de R${pot:.2f} entre {[j.jogador_id for j in contributors]}")
            prev_amount = amount
            remaining = [(j, a) for j, a in remaining if a > amount]

        return side_pots

    def _identificar_vencedores(self, resultados: List[Tuple[JogadorNaMesa, Tuple[int, List[int]]]]) -> List[JogadorNaMesa]:
        resultados.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)
        melhor = resultados[0][1]
        return [j for j, r in resultados if r == melhor]

    def atualizar_pote_total(self):
        debug_print(f"[ATUALIZAR_POTE_TOTAL] Atualizando pote na mesa {self.mesa.id}")
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )
        # debug: lista de apostas atuais por jogador antes da soma
        debug_print(f"[ATUALIZAR_POTE_TOTAL] apostas antes de somar: {[ (j.jogador_id, j.aposta_atual) for j in jogadores ]}")
        total = sum(j.aposta_atual for j in jogadores)
        # debug: valor total calculado
        debug_print(f"[ATUALIZAR_POTE_TOTAL] soma calculada: R${total:.2f}")
        self.mesa.pote_total += total
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"[ATUALIZAR_POTE_TOTAL] Adicionado R${total:.2f} ao pote. Total agora R${self.mesa.pote_total:.2f}")

    async def distribuir_pote(self, vencedor: JogadorNaMesa):
        from panopoker.poker.models.mesa import EstadoDaMesa
        vencedor = self.db.merge(vencedor)
        self.db.refresh(self.mesa)

        if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP and self.mesa.pote_total == 0:
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

