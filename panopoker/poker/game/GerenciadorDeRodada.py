from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa
from typing import Optional
import asyncio
from panopoker.core.timers_async import timers_async, loop_principal
import panopoker.core.timers_async as timers
from time import time
from fastapi import HTTPException
import json

from panopoker.websocket.manager import connection_manager

def marcar_como_ausente(jogador: JogadorNaMesa):
    jogador.participando_da_rodada = False
    jogador.rodada_ja_agiu = True
    jogador.foldado = True
    jogador.aposta_atual = 0

def esta_fora_da_rodada(jogador: JogadorNaMesa):
    return (jogador.saldo_atual <= 0 and jogador.aposta_atual == 0 and not jogador.rodada_ja_agiu)


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

    async def avancar_vez(self, posicao_origem: Optional[int] = None, skip_timer=False):
        debug_print(f"[DEBUG] skip_timer={skip_timer}")
        debug_print("🔄 [avancar_vez] Iniciando avanço da vez")
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
            debug_print(f"⚠️ [avancar_vez] Apenas {len(ativos)} jogador(es) ativo(s), nada para avançar")
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)
            self.db.commit()
            self.db.refresh(self.mesa)
            return

        posicoes = [j.posicao_cadeira for j in ativos]
        mapa = {j.posicao_cadeira: j for j in ativos}

        # Define o ponto de partida para procurar próximo jogador
        if posicao_origem is None:
            atual = next((j for j in ativos if j.jogador_id == self.mesa.jogador_da_vez), None)
            posicao_origem = atual.posicao_cadeira if atual else posicoes[0]
            debug_print(f"▶️ [avancar_vez] Posicao origem não informada, usando {posicao_origem}")

        if posicao_origem in posicoes:
            idx = posicoes.index(posicao_origem)
        else:
            menores = [p for p in posicoes if p < posicao_origem]
            start = menores[-1] if menores else posicoes[-1]
            idx = posicoes.index(start)
            debug_print(f"▶️ [avancar_vez] Posicao origem ajustada para {posicoes[idx]}")

        # Debug estado dos jogadores antes de decidir próximo a agir
        debug_print("[avancar_vez] Estado dos jogadores ativos:")
        for j in ativos:
            debug_print(f" - Jogador {j.jogador_id} | pos {j.posicao_cadeira} | rodada_ja_agiu={j.rodada_ja_agiu} | saldo={j.saldo_atual} | aposta_atual={j.aposta_atual}")

        # Procura próximo jogador que NÃO agiu e tem saldo > 0
        for i in range(len(posicoes)):
            candidato = mapa[posicoes[(idx + i + 1) % len(posicoes)]]
            if not candidato.rodada_ja_agiu and candidato.saldo_atual > 0:
                self.mesa.jogador_da_vez = candidato.jogador_id

                if not skip_timer:
                    self.mesa.timestamp_inicio_rodada = int(time() * 1000)  # timestamp em milissegundos
                    debug_print(f"⏱️ [avancar_vez] [STAMP] Timer iniciado em {self.mesa.timestamp_inicio_rodada}")

                self.db.add(self.mesa)
                self.db.commit()
                self.db.refresh(self.mesa)
                debug_print(f"▶️ [avancar_vez] Vez para jogador {candidato.jogador_id} (pos {candidato.posicao_cadeira})")
                if not skip_timer:
                    self.iniciar_timer_vez(candidato.jogador_id)
                return

        # Se chegou aqui, todos agiram (rodada_ja_agiu=True) ou estão all-in (saldo 0)
        debug_print("[avancar_vez] Todos já agiram ou estão all-in, verificando apostas para evitar erro de fim prematuro")

        apostas = {j.aposta_atual for j in ativos}
        # Se apostas diferentes, dá reset na rodada_ja_agiu do jogador com menor aposta pra ele agir de novo
        if len(apostas) > 1 and all(j.rodada_ja_agiu for j in ativos):
            menor_aposta = min(apostas)
            debug_print(f"[avancar_vez] Apostas diferentes detectadas: {apostas}. Resetando rodada_ja_agiu do jogador com menor aposta ({menor_aposta})")
            for j in ativos:
                if j.aposta_atual == menor_aposta:
                    j.rodada_ja_agiu = False
                    self.db.add(j)
            self.db.commit()
            # Recursivamente chama avancar_vez para atualizar a vez após reset
            await self.avancar_vez(posicao_origem=None, skip_timer=skip_timer)
            return

        debug_print("✅ [avancar_vez] Todos agiram ou sem saldo — fim de rodada")
        self.mesa.jogador_da_vez = None
        self.db.add(self.mesa)
        self.db.commit()
        self.db.refresh(self.mesa)

        if not skip_timer:
            await self.verificar_proxima_etapa()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "vez_atualizada",
            "jogador_id": self.mesa.jogador_da_vez,
            "vez_timestamp": self.mesa.timestamp_inicio_rodada
        })

    async def verificar_proxima_etapa(self, posicao_origem: Optional[int] = None):
        debug_print("🔎 [verificar_proxima_etapa] Verificando próxima etapa da rodada")

        ativos = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False
            )
            .all()
        )

        debug_print(f"[verificar_proxima_etapa] Jogadores ativos: {[j.jogador_id for j in ativos]}")

        # Vitória automática se só sobrar 1
        if len(ativos) == 1:
            vencedor = ativos[0]
            debug_print(f"🏆 [verificar_proxima_etapa] Vitória automática: jogador {vencedor.jogador_id}")
            self._distribuidor().atualizar_pote_total()
            await self._distribuidor().distribuir_pote(vencedor)
            await connection_manager.broadcast_mesa(
                self.mesa.id,
                {"evento": "vitoria_automatica", "jogador_id": vencedor.jogador_id}
            )
            await self._resetador().nova_rodada()
            return

        # Showdown imediato se todos zeraram o saldo
        if ativos and all(j.saldo_atual == 0 for j in ativos):
            debug_print("🏁 [verificar_proxima_etapa] Todos sem saldo — showdown imediato")
            await self._distribuidor().realizar_showdown()
            return

        # Avança fase NORMAL só quando:
        # - TODOS já agiram
        # - As apostas estão todas iguais
        # - NINGUÉM está all-in (saldo > 0 pra todos)
        apostas_ativos = {j.aposta_atual for j in ativos}
        if (
            all(j.rodada_ja_agiu for j in ativos)
            and len(apostas_ativos) == 1
            and all(j.saldo_atual > 0 for j in ativos)
        ):
            debug_print("⏭️ [verificar_proxima_etapa] Todos agiram e apostas iguais (sem all-in) — avançar fase")
            await self.avancar_fase()
            return

        # Showdown imediato se rolou all-in + call
        if (
            all(j.rodada_ja_agiu or j.saldo_atual == 0 for j in ativos)
            and len(apostas_ativos) == 1
        ):
            debug_print("🏁 [verificar_proxima_etapa] All-in + call detectado — showdown imediato")
            await self._distribuidor().realizar_showdown()
            return

        # Showdown de side-pot extremo: alguém all-in e ninguém mais pode agir
        if (
            any(j.saldo_atual == 0 for j in ativos)
            and not any((not j.rodada_ja_agiu) and j.saldo_atual > 0 for j in ativos)
        ):
            debug_print("🏁 [verificar_proxima_etapa] Side-pot completo — showdown imediato")
            await self._distribuidor().realizar_showdown()
            return

        # Caso normal: repassa vez ou inicia vez padrão
        if posicao_origem is not None:
            debug_print(f"↪️ [verificar_proxima_etapa] Repassar vez de posição {posicao_origem}")
            await self.avancar_vez(posicao_origem, skip_timer=False)
        else:
            debug_print("↪️ [verificar_proxima_etapa] Iniciando vez padrão")
            await self.avancar_vez()

    async def avancar_fase(self):
        from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
        debug_print(f"📈 [avancar_fase] Avançando fase atual: {self.mesa.estado_da_rodada}")

        self._distribuidor().atualizar_pote_total()

        # Define próxima fase
        if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.FLOP
        elif self.mesa.estado_da_rodada == EstadoDaMesa.FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.TURN
        elif self.mesa.estado_da_rodada == EstadoDaMesa.TURN:
            self.mesa.estado_da_rodada = EstadoDaMesa.RIVER
        else:
            debug_print("🎬 Showdown")
            await self._distribuidor().realizar_showdown()
            return

        self.mesa.aposta_atual = 0.0
        self.db.add(self.mesa)

        # Reset flags dos jogadores para a nova fase
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )

        for j in jogadores:
            j.rodada_ja_agiu = False
            j.aposta_atual = 0.0
            self.db.add(j)

        self.db.commit()

        debug_print(f"🔄 [avancar_fase] Nova fase: {self.mesa.estado_da_rodada}")

        self._preparador().definir_primeiro_a_agir()

        comunitarias = (
            self.mesa.cartas_comunitarias
            if isinstance(self.mesa.cartas_comunitarias, dict)
            else json.loads(self.mesa.cartas_comunitarias)
        )

        novas_cartas = []
        if self.mesa.estado_da_rodada == EstadoDaMesa.FLOP:
            novas_cartas = comunitarias.get("flop", [])
        elif self.mesa.estado_da_rodada == EstadoDaMesa.TURN:
            turn = comunitarias.get("turn")
            if turn:
                novas_cartas = [turn]
        elif self.mesa.estado_da_rodada == EstadoDaMesa.RIVER:
            river = comunitarias.get("river")
            if river:
                novas_cartas = [river]

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "fase_avancada",
            "estado_rodada": self.mesa.estado_da_rodada,
            "novas_cartas": novas_cartas
        })

    def iniciar_timer_vez(self, jogador_id: int):
        old = timers_async.get(self.mesa.id)
        if old and not old.done():
            old.cancel()
            debug_print(f"❌ [iniciar_timer_vez] Cancelando timer anterior da mesa {self.mesa.id}")

        debug_print(f"⏳ [iniciar_timer_vez] Iniciando timer async para jogador {jogador_id} na mesa {self.mesa.id}")
        future = asyncio.run_coroutine_threadsafe(
            self._timer_coroutine(jogador_id),
            self.loop
        )
        timers_async[self.mesa.id] = future

    def cancelar_timer(self):
        old = timers_async.pop(self.mesa.id, None)
        if old and not old.done():
            old.cancel()
            debug_print(f"❌ [cancelar_timer] Timer da mesa {self.mesa.id} cancelado")

    async def _timer_coroutine(self, jogador_id: int):
        debug_print(f"🟡 [_timer_coroutine] Entrando no timer do jogador {jogador_id}")
        try:
            await asyncio.sleep(20)
        except asyncio.CancelledError:
            debug_print(f"❌ [_timer_coroutine] Timer CANCELADO para jogador {jogador_id}")
            return

        debug_print(f"🟢 [_timer_coroutine] Timer terminou — forçando fold do jogador {jogador_id}")
        try:
            await self._chamar_fold().acao_fold(jogador_id)
        except HTTPException as e:
            debug_print(f"[TIMER] Não consegui forçar fold: {e.detail}")
