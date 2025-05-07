from sqlalchemy.orm import Session
from app.core.debug import debug_print
from app.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa
from typing import Optional
import asyncio
import time
from app.core.timers_async import timers_async, loop_principal

class GerenciadorDeRodada:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db

    def _resetador(self):
        from app.game.poker.ResetadorDePartida import ResetadorDePartida
        return ResetadorDePartida(self.mesa, self.db)

    def _distribuidor(self):
        from app.game.poker.DistribuidorDePote import DistribuidorDePote
        return DistribuidorDePote(self.mesa, self.db)

    def _preparador(self):
        from app.game.poker.PreparadorDeRodada import PreparadorDeRodada
        return PreparadorDeRodada(self.mesa, self.db)

    def avancar_vez(self, posicao_origem: Optional[int] = None):
        debug_print("🔄 Avançar vez")
        # todos os que participam e não foldaram
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

        # definir ponto de partida
        if posicao_origem is None:
            atual = next((j for j in ativos if j.jogador_id == self.mesa.jogador_da_vez), None)
            posicao_origem = atual.posicao_cadeira if atual else posicoes[0]
        idx = posicoes.index(posicao_origem) if posicao_origem in posicoes else 0

        # percorre o “ciclo” pulando quem já agiu ou estiver sem saldo
        for i in range(1, len(posicoes) + 1):
            candidato = mapa[posicoes[(idx + i) % len(posicoes)]]
            if candidato.rodada_ja_agiu or candidato.saldo_atual <= 0:
                continue

            # encontrou quem deve agir
            self.mesa.jogador_da_vez = candidato.jogador_id
            self.db.add(self.mesa); self.db.commit()
            debug_print(f"▶️ Vez para jogador {candidato.jogador_id} (pos {candidato.posicao_cadeira})")
            self.iniciar_timer_vez(candidato.jogador_id)
            return

        # nenhum disponível → rodada encerrada
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

        # vitória automática
        if len(ativos) == 1:
            vencedor = ativos[0]
            debug_print(f"🏆 Vitória automática: jogador {vencedor.jogador_id}")
            self._distribuidor().distribuir_pote(vencedor)
            self._resetador().nova_rodada()
            return
        
        # Se todos estão sem saldo_atual restante (depois de todo for allin por ex) → showdown imediato
        if ativos and all(j.saldo_atual == 0 for j in ativos):
            debug_print("🏁 Todos sem saldo restante — showdown imediato")
            self._distribuidor().realizar_showdown()
            return

        # considera all-in como já tendo agido
        def ja_agiu(j):
            return j.rodada_ja_agiu or (j.saldo_atual == 0 and j.aposta_atual > 0)

        apostas = {j.aposta_atual for j in ativos}
        if all(ja_agiu(j) for j in ativos) and len(apostas) == 1:
            debug_print("⏭️ Todos agiram/all-in e apostas iguais — avançar fase")
            self.avancar_fase()
            return

        if posicao_origem is not None:
            debug_print(f"↪️ Repassar vez de posição {posicao_origem}")
            self.avancar_vez(posicao_origem)
            if self.mesa.jogador_da_vez is None:
                debug_print("⚠️ Ninguém recebeu vez — avançar fase")
                self.avancar_fase()
            return

        debug_print("➡️ Avançar vez genérico")
        self.avancar_vez()

    def avancar_fase(self):
        debug_print(f"📈 Avançar fase ({self.mesa.estado_da_rodada})")

        if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.FLOP
        elif self.mesa.estado_da_rodada == EstadoDaMesa.FLOP:
            self.mesa.estado_da_rodada = EstadoDaMesa.TURN
        elif self.mesa.estado_da_rodada == EstadoDaMesa.TURN:
            self.mesa.estado_da_rodada = EstadoDaMesa.RIVER
        else:
            debug_print("🎬 Showdown")
            self._distribuidor().realizar_showdown()
            return

        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False
            )
            .all()
        )

        # 🟢 Coleta as apostas da fase antes de resetar
        valor_pote = sum(j.aposta_atual for j in jogadores if j.aposta_atual)
        self.mesa.pote_total += round(valor_pote, 2)
        debug_print(f"[AVANCAR_FASE] Coletado R${valor_pote:.2f} para o pote")

        # reset de apostas no início de cada street
        self.mesa.aposta_atual = 0.0
        self.db.add(self.mesa)

        for j in jogadores:
            j.rodada_ja_agiu = False
            j.aposta_atual = 0.0
            self.db.add(j)

        self.db.commit()

        debug_print(f"🔄 Nova fase: {self.mesa.estado_da_rodada}")
        self._preparador().definir_primeiro_a_agir()
    
        # 🧠 Corrigir: timer não estava iniciando após definir novo jogador da vez
        if self.mesa.jogador_da_vez:
            self.iniciar_timer_vez(self.mesa.jogador_da_vez)



    def iniciar_timer_vez(self, jogador_id: int):
        self.cancelar_timer()
        debug_print(f"⏳ Timer async iniciado para jogador {jogador_id}")

        future = asyncio.run_coroutine_threadsafe(
            self._timer_coroutine(jogador_id),
            loop_principal
        )
        timers_async[self.mesa.id] = future


    def cancelar_timer(self):
        if self.mesa.id in timers_async:
            timers_async[self.mesa.id].cancel()
            del timers_async[self.mesa.id]
            debug_print(f"[TIMER CANCELADO] Timer da mesa {self.mesa.id} foi cancelado com sucesso")
        else:
            debug_print(f"[TIMER CANCELADO] Nenhum timer ativo para a mesa {self.mesa.id}")


    async def _timer_coroutine(self, jogador_id: int):
        debug_print(f"🟡 Entrando no timer do jogador {jogador_id}")
        await asyncio.sleep(20)
        debug_print(f"🟢 Timer terminou — validando jogador {jogador_id}")

        jogador = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.jogador_id == jogador_id,
                JogadorNaMesa.mesa_id == self.mesa.id
            )
            .first()
        )
        if not jogador:
            debug_print(f"[TIMER] Jogador {jogador_id} não encontrado")
            return
        if self.mesa.jogador_da_vez != jogador_id:
            debug_print(f"[TIMER] Jogador {jogador_id} não é mais o da vez — ignorado")
            return

        debug_print(f"⏱️ Tempo esgotado — forçando fold do jogador {jogador_id}")
        jogador.foldado = True
        self.db.add(jogador)
        self.db.commit()
        time.sleep(0.05)
        self.verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)
