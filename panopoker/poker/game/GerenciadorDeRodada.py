from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa
from typing import Optional
import asyncio
from panopoker.core.timers_async import timers_async, loop_principal
import panopoker.core.timers_async as timers
from fastapi import HTTPException

class GerenciadorDeRodada:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db
        self.loop = loop_principal

    def _resetador(self):
        from panopoker.poker.game.ResetadorDePartida import ResetadorDePartida
        return ResetadorDePartida(self.mesa, self.db)

    def _distribuidor(self):
        from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
        return DistribuidorDePote(self.mesa, self.db)

    def _preparador(self):
        from panopoker.poker.game.PreparadorDeRodada import PreparadorDeRodada
        return PreparadorDeRodada(self.mesa, self.db)
    
    def _chamar_fold(self):
        from panopoker.poker.game.ExecutorDeAcoes import ExecutorDeAcoes
        return ExecutorDeAcoes(self.mesa, self.db)













    def avancar_vez(self, posicao_origem: Optional[int] = None, skip_timer = False):
        debug_print("🔄 Avançar vez")
        ativos = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False
            )
            .order_by(JogadorNaMesa.posicao_cadeira)
            .all()
        )
        if len(ativos) <= 1:
            debug_print("⚠️ Menos de dois ativos — nada a avançar")
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa); self.db.commit()
            return

        posicoes = [j.posicao_cadeira for j in ativos]
        mapa = {j.posicao_cadeira: j for j in ativos}

        if posicao_origem is None:
            atual = next((j for j in ativos if j.jogador_id == self.mesa.jogador_da_vez), None)
            posicao_origem = atual.posicao_cadeira if atual else posicoes[0]

        if posicao_origem in posicoes:
            idx = posicoes.index(posicao_origem)
        else:
            menores = [p for p in posicoes if p < posicao_origem]
            start = menores[-1] if menores else posicoes[-1]
            idx = posicoes.index(start)

        for i in range(len(posicoes)):
            candidato = mapa[posicoes[(idx + i + 1) % len(posicoes)]]
            if candidato.rodada_ja_agiu or candidato.saldo_atual <= 0:
                continue

            self.mesa.jogador_da_vez = candidato.jogador_id
            self.db.add(self.mesa); self.db.commit()
            debug_print(f"▶️ Vez para jogador {candidato.jogador_id} (pos {candidato.posicao_cadeira})")
            return

        debug_print("✅ Todos agiram ou sem saldo — fim de rodada")
        self.mesa.jogador_da_vez = None
        self.db.add(self.mesa); self.db.commit()











    def verificar_proxima_etapa(self, posicao_origem: Optional[int] = None):
        debug_print("🔎 Verificando próxima etapa")

        ativos = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False
            )
            .all()
        )

        # 🏆 Vitória automática
        if len(ativos) == 1:
            vencedor = ativos[0]
            debug_print(f"🏆 Vitória automática: jogador {vencedor.jogador_id}")
            self._distribuidor().atualizar_pote_total()
            self._distribuidor().distribuir_pote(vencedor)
            self._resetador().nova_rodada()
            return

        # 🏁 Todos sem saldo — showdown imediato
        if ativos and all(j.saldo_atual == 0 for j in ativos):
            debug_print("🏁 Todos sem saldo restante — showdown imediato")
            self._distribuidor().realizar_showdown()
            return

        # ✅ Todos agiram ou estão all-in + apostas iguais → avançar fase
        if all(j.rodada_ja_agiu or (j.saldo_atual == 0 and j.aposta_atual > 0) for j in ativos) and len({j.aposta_atual for j in ativos}) == 1:
            debug_print("⏭️ Todos agiram/all-in e apostas iguais — avançar fase")
            self.avancar_fase()
            return

        # 🔁 Repassar vez
        if posicao_origem is not None:
            debug_print(f"↪️ Repassar vez de posição {posicao_origem}")
            self.avancar_vez(posicao_origem, skip_timer=True)
        else:
            self.avancar_vez()

        # ⚠️ Ninguém recebeu vez
        if self.mesa.jogador_da_vez is None:
            debug_print("⚠️ Ninguém recebeu vez — avançar fase")
            self.avancar_fase()
            return

        # ⏳ Timer do novo jogador da vez
        self.iniciar_timer_vez(self.mesa.jogador_da_vez)















    def avancar_fase(self):
        from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
        debug_print(f"📈 Avançar fase ({self.mesa.estado_da_rodada})")

        DistribuidorDePote(self.mesa, self.db).atualizar_pote_total()

        # muda o estado da rodada
        if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.FLOP
        elif self.mesa.estado_da_rodada == EstadoDaMesa.FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.TURN
        elif self.mesa.estado_da_rodada == EstadoDaMesa.TURN:
            self.mesa.estado_da_rodada = EstadoDaMesa.RIVER
        else:
            debug_print("🎬 Showdown")
            # passa pra DistribuidorDePote cuidar do showdown e do pote
            self._distribuidor().realizar_showdown()
            return

        self.mesa.aposta_atual = 0.0
        self.db.add(self.mesa)

        # zera flags de ação e apostas para o início da nova street
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )
        for j in jogadores:
            j.rodada_ja_agiu = False
            j.aposta_atual = 0.0
            self.db.add(j)

        # persiste a mudança de fase + resets
        self.db.add(self.mesa)
        self.db.commit()

        debug_print(f"🔄 Nova fase: {self.mesa.estado_da_rodada}")
        # define quem começa a agir na street atual
        self._preparador().definir_primeiro_a_agir()























    def iniciar_timer_vez(self, jogador_id: int):
        # cancela o timer anterior desta mesa
        old = timers_async.get(self.mesa.id)
        if old and not old.done():
            old.cancel()
            debug_print(f"❌ Cancelando timer anterior da mesa {self.mesa.id}")

        debug_print(f"⏳ Iniciando timer async para jogador {jogador_id} na mesa {self.mesa.id}")
        future = asyncio.run_coroutine_threadsafe(
            self._timer_coroutine(jogador_id),
            self.loop
        )
        timers_async[self.mesa.id] = future





    def cancelar_timer(self):
        # cancela o timer desta mesa
        old = timers_async.pop(self.mesa.id, None)
        if old and not old.done():
            old.cancel()
            debug_print(f"❌ Timer da mesa {self.mesa.id} cancelado")





    async def _timer_coroutine(self, jogador_id: int):
        debug_print(f"🟡 Entrando no timer do jogador {jogador_id}")
        try:
            await asyncio.sleep(20)
        except asyncio.CancelledError:
            debug_print(f"❌ Timer CANCELADO para jogador {jogador_id}")
            return

        debug_print(f"🟢 Timer terminou — forçando fold do jogador {jogador_id}")
        try:
            self._chamar_fold().acao_fold(jogador_id)
        except HTTPException as e:
            debug_print(f"[TIMER] Não consegui forçar fold: {e.detail}")


