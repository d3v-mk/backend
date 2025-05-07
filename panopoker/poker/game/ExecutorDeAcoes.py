from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.models.mesa import Mesa, JogadorNaMesa
from fastapi import HTTPException


class ExecutorDeAcoes:
    def __init__(self, mesa: Mesa, db: Session):
        debug_print(f"[ExecutorDeAcoes] iniciando para mesa {mesa.id}")
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

    def acao_check(self, jogador_id: int):
        self._cancelar_timer()
        debug_print(f"[ACAO_CHECK] início para jogador {jogador_id}")
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.foldado or not jogador.participando_da_rodada:
            raise HTTPException(400, "Jogador não pode agir.")
        if self.mesa.aposta_atual > 0 and not abs(jogador.aposta_atual - self.mesa.aposta_atual) < 1e-6:
            raise HTTPException(400, "CHECK inválido: aposte ou all-in primeiro.")

        jogador.rodada_ja_agiu = True
        self.db.commit()
        debug_print(f"[ACAO_CHECK] jogador {jogador_id} deu CHECK")
        self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)

    def acao_call(self, jogador_id: int):
        self._cancelar_timer()
        debug_print(f"[ACAO_CALL] início para jogador {jogador_id}")
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
        jogador.aposta_atual += paid
        jogador.rodada_ja_agiu = True
        #self.mesa.pote_total += paid
        self.db.commit()

        debug_print(f"[ACAO_CALL] jogador {jogador_id} pagou {paid}")
        self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)

    def acao_allin(self, jogador_id: int):
        self._cancelar_timer()
        debug_print(f"[ACAO_ALLIN] início para jogador {jogador_id}")
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.rodada_ja_agiu or jogador.foldado or not jogador.participando_da_rodada or jogador.saldo_atual <= 0:
            raise HTTPException(400, "Jogador não pode agir.")

        allin = jogador.saldo_atual
        jogador.aposta_atual += allin
        jogador.saldo_atual = 0.0
        jogador.rodada_ja_agiu = True

        is_raise = False
        if jogador.aposta_atual > self.mesa.aposta_atual:
            self.mesa.aposta_atual = jogador.aposta_atual
            is_raise = True

        #self.mesa.pote_total += allin

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
        debug_print(f"[ACAO_ALLIN] jogador {jogador_id} ALL-IN {allin}")
        self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)

    def acao_fold(self, jogador_id: int):
        self._cancelar_timer()
        debug_print(f"[ACAO_FOLD] início para jogador {jogador_id}")
        jogador = self._buscar_jogador(jogador_id)

        if jogador.jogador_id != self.mesa.jogador_da_vez:
            raise HTTPException(400, "Não é sua vez de agir.")
        if jogador.rodada_ja_agiu or jogador.foldado or not jogador.participando_da_rodada:
            raise HTTPException(400, "Jogador não pode agir.")

        jogador.foldado = True
        jogador.participando_da_rodada = False
        jogador.rodada_ja_agiu = True
        self.mesa.jogador_da_vez = None
        self.db.commit()

        debug_print(f"[ACAO_FOLD] jogador {jogador_id} deu FOLD")
        self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)

    def acao_raise(self, jogador_id: int, valor: float):
        self._cancelar_timer()
        debug_print(f"[ACAO_RAISE] início para jogador {jogador_id} valor {valor}")
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
        jogador.aposta_atual = novo_total
        jogador.rodada_ja_agiu = True

        self.mesa.aposta_atual = novo_total
        #self.mesa.pote_total += total_aposta

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
        debug_print(f"[ACAO_RAISE] jogador {jogador_id} RAISE de {valor}")
        self._gerenciador().verificar_proxima_etapa(posicao_origem=jogador.posicao_cadeira)
