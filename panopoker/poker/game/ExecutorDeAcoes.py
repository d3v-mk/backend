from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from fastapi import HTTPException
from panopoker.websocket.manager import connection_manager


class ExecutorDeAcoes:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db

    def _cancelar_timer(self):
        from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada  # lazy import evita loop
        gerente = GerenciadorDeRodada(self.mesa, self.db)
        gerente.cancelar_timer()

    def _gerenciador(self):
        from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada
        return GerenciadorDeRodada(self.mesa, self.db)

    def _buscar_jogador(self, jogador_id: int) -> JogadorNaMesa:
        jogador = (
            self.db.query(JogadorNaMesa)
            .filter_by(mesa_id=self.mesa.id, jogador_id=jogador_id)
            .first()
        )
        if not jogador:
            debug_print(f"[ExecutorDeAcoes] jogador {jogador_id} não encontrado")
            raise HTTPException(status_code=404, detail="Jogador não encontrado na mesa.")
        return jogador
    









    async def acao_check(self, jogador_id: int):
        debug_print(f"[ACAO_CHECK] 🔍 Iniciando CHECK do jogador {jogador_id}")
        
        jogador = self._buscar_jogador(jogador_id)
        debug_print(f"[ACAO_CHECK] 👤 Jogador encontrado: {jogador.jogador_id} (posição {jogador.posicao_cadeira})")

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            debug_print(f"[ACAO_CHECK] ❌ Jogador {jogador.jogador_id} tentou agir fora da vez (vez do jogador {self.mesa.jogador_da_vez})")
            raise HTTPException(400, "Não é sua vez de agir.")

        if jogador.foldado or not jogador.participando_da_rodada:
            debug_print(f"[ACAO_CHECK] ❌ Jogador {jogador.jogador_id} está foldado ou fora da rodada")
            raise HTTPException(400, "Jogador não pode agir.")

        if self.mesa.aposta_atual > 0 and not abs(jogador.aposta_atual - self.mesa.aposta_atual) < 1e-6:
            debug_print(f"[ACAO_CHECK] ❌ CHECK inválido: aposta atual da mesa = {self.mesa.aposta_atual}, aposta do jogador = {jogador.aposta_atual}")
            raise HTTPException(400, "CHECK inválido: aposte ou all-in primeiro.")

        self._cancelar_timer()
        debug_print(f"[ACAO_CHECK] ⏹️ Timer cancelado para jogador {jogador_id}")

        jogador.rodada_ja_agiu = True
        self.db.commit()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })

        debug_print(f"[ACAO_CHECK] ✅ Jogador {jogador_id} deu CHECK com sucesso")

        await self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)
        debug_print(f"[ACAO_CHECK] 🔄 Chamando verificar_proxima_etapa() após CHECK do jogador {jogador_id}")





    async def acao_call(self, jogador_id: int):
        from panopoker.poker.game.GerenciadorDeRodada import esta_fora_da_rodada, marcar_como_ausente
        debug_print(f"[ACAO_CALL] jogador {jogador_id} tentando CALL")
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.rodada_ja_agiu or jogador.foldado or not jogador.participando_da_rodada:
            raise HTTPException(400, "Jogador não pode agir.")

        to_pay = self.mesa.aposta_atual - jogador.aposta_atual
        if abs(to_pay) < 1e-6:
            raise HTTPException(400, "Nada para pagar. Use CHECK.")
        if jogador.saldo_atual <= 0:
            raise HTTPException(400, "Saldo insuficiente para CALL.")

        paid = min(jogador.saldo_atual, to_pay)
        jogador.saldo_atual -= paid
        jogador.saldo_atual = round(jogador.saldo_atual, 2)
        jogador.aposta_atual += paid
        jogador.aposta_acumulada += paid
        jogador.rodada_ja_agiu = True

        self._cancelar_timer()
        debug_print(f"[ACAO_CALL] ❌ Timer cancelado para jogador {jogador_id}")

        self.db.commit()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })

        await self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)











    async def acao_allin(self, jogador_id: int):
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.rodada_ja_agiu or jogador.foldado or not jogador.participando_da_rodada or jogador.saldo_atual <= 0:
            raise HTTPException(400, "Jogador não pode agir.")

        allin = jogador.saldo_atual
        jogador.aposta_atual += allin
        jogador.aposta_acumulada += allin
        jogador.saldo_atual = 0.0
        jogador.saldo_atual = round(jogador.saldo_atual, 2)
        jogador.rodada_ja_agiu = True
        self._cancelar_timer()

        debug_print(f"[ACAO_ALLIN_SALDO_ATUAL] Saldo do jogador {jogador_id} depois do allin: {jogador.saldo_atual}")

        is_raise = False
        if jogador.aposta_atual > self.mesa.aposta_atual:
            self.mesa.aposta_atual = jogador.aposta_atual
            is_raise = True

        if is_raise:
            outros = (
                self.db.query(JogadorNaMesa)
                .filter(
                    JogadorNaMesa.mesa_id == self.mesa.id,
                    JogadorNaMesa.participando_da_rodada == True,
                    JogadorNaMesa.foldado == False,
                    JogadorNaMesa.jogador_id != jogador_id
                )
                .all()
            )
            for o in outros:
                o.rodada_ja_agiu = False

        self.db.commit()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })
        
        debug_print(f"[ACAO_ALLIN] jogador {jogador_id} ALL-IN {allin}")
        await self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)








    async def acao_fold(self, jogador_id: int):
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.rodada_ja_agiu or jogador.foldado or not jogador.participando_da_rodada:
            raise HTTPException(400, "Jogador não pode agir.")

        jogador.foldado = True
        jogador.participando_da_rodada = False
        jogador.rodada_ja_agiu = True
        self.mesa.jogador_da_vez = None
        self._cancelar_timer()
        self.db.commit()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })

        debug_print(f"[ACAO_FOLD] jogador {jogador_id} deu FOLD")
        await self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)







    async def acao_raise(self, jogador_id: int, valor: float):
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.foldado or not jogador.participando_da_rodada or valor <= 0:
            raise HTTPException(400, "Jogador não pode agir.")

        to_call = self.mesa.aposta_atual - jogador.aposta_atual
        if jogador.saldo_atual < to_call + valor:
            raise HTTPException(400, "Saldo insuficiente para CALL+RAISE.")

        novo_total = self.mesa.aposta_atual + valor
        total_aposta = to_call + valor

        jogador.saldo_atual -= total_aposta
        jogador.saldo_atual = round(jogador.saldo_atual, 2)
        jogador.aposta_atual = novo_total
        jogador.aposta_acumulada += total_aposta
        jogador.rodada_ja_agiu = True

        debug_print(f"[ACAO_RAISE_SALDO_ATUAL] Saldo do jogador {jogador_id} depois do raise: {jogador.saldo_atual}")

        self.mesa.aposta_atual = novo_total
        self._cancelar_timer()

        outros = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False,
                JogadorNaMesa.jogador_id != jogador_id
            )
            .all()
        )
        for o in outros:
            o.rodada_ja_agiu = False

        self.db.commit()

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })

        debug_print(f"[ACAO_RAISE_APOSTA_ATUAL] jogador {jogador_id} RAISE de {valor}")
        await self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)


