from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import Session
from fastapi import HTTPException
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import MesaStatus
from panopoker.websocket.manager import connection_manager
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
import json

class ControladorDeMesa:
    def __init__(self, mesa: Mesa, db: Session):
        self.db = db
        self.mesa = mesa

    def _controlador(self):
        from panopoker.poker.game.ControladorDePartida import ControladorDePartida
        return ControladorDePartida(self.mesa, self.db)
    
    def _gerenciador(self):
        from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada
        return GerenciadorDeRodada(self.mesa, self.db)
    
    def _distribuidor(self):
        from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
        return DistribuidorDePote(self.mesa, self.db)
    
    def _resetador (self):
        from panopoker.poker.game.ResetadorDePartida import ResetadorDePartida
        return ResetadorDePartida(self.mesa, self.db)
    

    def verificar_vitoria_automatica(self):
        ativos = self.db.query(JogadorNaMesa) \
            .filter(JogadorNaMesa.mesa_id == self.mesa.id,
                    JogadorNaMesa.participando_da_rodada == True,
                    JogadorNaMesa.foldado == False,
                    JogadorNaMesa.saldo_atual > 0) \
            .all()

        if len(ativos) == 1:
            vencedor = ativos[0]
            debug_print(f"[VITORIA_AUTOMATICA] Apenas {vencedor.jogador_id} participando — vitória automática!")

            from panopoker.poker.game.DistribuidorDePote import DistribuidorDePote
            from panopoker.poker.game.ResetadorDePartida import ResetadorDePartida

            distribuidor = DistribuidorDePote(self.mesa, self.db)
            distribuidor.distribuir_pote(vencedor)

            resetador = ResetadorDePartida(self.mesa, self.db)
            resetador.nova_rodada()

            return True  # vitória automática ocorreu

        return False  # sem vitória automática




    async def entrar_na_mesa(self, usuario: Usuario):
        print(f"[PRINT] === INICIANDO entrar_na_mesa ===")
        print(f"[PRINT] Mesa: {self.mesa.id} | Usuário: {usuario.id}")

        # 🔒 BLOQUEIO se mesa estiver em manutenção
        status_atual = MesaStatus(self.mesa.status) if isinstance(self.mesa.status, str) else self.mesa.status
        if status_atual == MesaStatus.manutencao:
            print(f"[PRINT] ⚠️ Mesa está em manutenção! ABORTANDO")
            raise HTTPException(status_code=403, detail="A mesa está em manutenção no momento.")

        jogador_existente = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .filter(JogadorNaMesa.jogador_id == usuario.id)\
            .first()

        print(f"[PRINT] Jogador já existe? {'SIM' if jogador_existente else 'NÃO'}")

        if jogador_existente:
            print(f"[PRINT] ⚠️ Jogador já está na mesa. ABORTANDO")
            raise HTTPException(status_code=400, detail="Jogador já está na mesa.")

        print(f"[PRINT] Saldo do usuário: {usuario.saldo} | Buy-in da mesa: {self.mesa.buy_in}")
        if usuario.saldo < self.mesa.buy_in:
            print(f"[PRINT] ❌ Saldo insuficiente! ABORTANDO")
            raise HTTPException(status_code=400, detail="Saldo insuficiente para entrar na mesa.")

        # Debitar o buy-in do saldo do usuário
        usuario.saldo -= self.mesa.buy_in
        self.db.add(usuario)
        print(f"[PRINT] Debitado buy-in. Novo saldo do usuário: {usuario.saldo}")

        # Pegar próxima posição livre
        posicao = self._cadeira_posicao_disponivel()
        print(f"[PRINT] Próxima posição disponível: {posicao}")

        jogador_na_mesa = JogadorNaMesa(
            mesa_id=self.mesa.id,
            jogador_id=usuario.id,
            saldo_inicial=self.mesa.buy_in,
            saldo_atual=self.mesa.buy_in,
            aposta_atual=0.0,
            foldado=False,
            posicao_cadeira=posicao,
            rodada_ja_agiu=False,
            participando_da_rodada=True,
            cartas=json.dumps([])
        )

        # AJUSTE IMPORTANTE: Se a mesa já estiver em jogo, jogador NÃO participa da rodada atual
        if self.mesa.status == MesaStatus.em_jogo:
            print("[PRINT] Mesa já está em jogo, não participa da rodada atual")
            jogador_na_mesa.participando_da_rodada = False
        else:
            print("[PRINT] Mesa NÃO está em jogo, já participa da rodada")
            jogador_na_mesa.participando_da_rodada = True

        self.db.add(jogador_na_mesa)
        print(f"[PRINT] Jogador adicionado no banco. Commitando...")
        self.db.commit()
        print(f"[PRINT] Commit realizado.")

        print(f"[PRINT] [ENTRAR_NA_MESA] Jogador {usuario.id} entrou na mesa {self.mesa.nome}")

        # Atualiza status da mesa se tiver pelo menos 2 jogadores
        jogadores = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .all()
        print(f"[PRINT] Total de jogadores na mesa: {len(jogadores)}")

        if len(jogadores) >= 2 and self.mesa.status == "aberta":
            print(f"[PRINT] Mesa aberta e já tem 2 jogadores ou mais. Iniciando partida...")
            self.db.refresh(self.mesa)
            controlador = self._controlador()
            await controlador.iniciar_partida()
            
        print(f"[PRINT] === FIM entrar_na_mesa ===")


            





    async def sair_da_mesa(self, usuario: Usuario):
        from panopoker.poker.game.GerenciadorDeRodada import marcar_como_ausente

        try:
            user_id = int(usuario.id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="ID de usuário inválido.")

        debug_print(f"[SAIR_DA_MESA] Tentando remover jogador {user_id} da mesa {self.mesa.id}")

        todos = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )
        debug_print(f"[SAIR_DA_MESA] IDs na mesa: {[j.jogador_id for j in todos]}")

        jogador = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.jogador_id == user_id
            )
            .first()
        )
        if not jogador:
            raise HTTPException(status_code=404, detail="Jogador não está na mesa.")

        if jogador.aposta_atual > 0:
            valor = jogador.aposta_atual
            debug_print(f"[SAIR_DA_MESA] Movendo R${valor:.2f} do jogador {user_id} direto para pote_total")
            self.mesa.pote_total = (self.mesa.pote_total or 0) + valor
            jogador.aposta_atual = 0
            self.db.add_all([self.mesa, jogador])
            self.db.commit()

        marcar_como_ausente(jogador)

        if jogador.saldo_atual > 0:
            debug_print(f"[SAIR_DA_MESA] Devolvendo R${jogador.saldo_atual:.2f} p/ usuário {user_id}")
            usuario.saldo += jogador.saldo_atual
            jogador.saldo_atual = 0
            self.db.add_all([usuario, jogador])

        self.db.commit()

        ativos = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True
            )
            .all()
        )

        if len(ativos) <= 1:
            self._gerenciador().cancelar_timer()

            if len(ativos) == 1 and self.mesa.status == MesaStatus.em_jogo:
                vencedor = ativos[0]
                debug_print(f"[SAIR_DA_MESA] Vitória automática para jogador {vencedor.jogador_id}")
                self._distribuidor().atualizar_pote_total()
                await self._distribuidor().distribuir_pote(vencedor)

            await self._resetador().nova_rodada()

            if not ativos:
                self.mesa.status = MesaStatus.aberta
                self.mesa.jogador_da_vez = None
                self.db.add(self.mesa)
                self.db.commit()
                debug_print(f"[SAIR_DA_MESA] Mesa {self.mesa.id} voltou para 'aberta' por falta de jogadores.")

            await connection_manager.broadcast_mesa(self.mesa.id, {
                "evento": "mesa_atualizada"
            })
            return

        if self.mesa.jogador_da_vez == user_id:
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)
            self.db.commit()
            await self._gerenciador().avancar_vez()

        # BROADCAST, mesmo que ainda tenha mais de um jogador
        debug_print(f"[SAIR_DA_MESA] Broadcast geral: mesa_atualizada após saída do jogador {user_id}")
        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })


    def desconectar_jogador(self, jogador_id: int):
        key = (self.mesa.id, jogador_id)
        if key in connection_manager.active_connections:
            ws_list = connection_manager.active_connections[key].copy()
            for ws in ws_list:
                connection_manager.disconnect(self.mesa.id, jogador_id, ws)


    def _cadeira_posicao_disponivel(self):
        jogadores = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .order_by(JogadorNaMesa.posicao_cadeira)\
            .all()

        ocupadas = [jogador.posicao_cadeira for jogador in jogadores if jogador.posicao_cadeira is not None]

        for pos in range(self.mesa.limite_jogadores):
            if pos not in ocupadas:
                return pos

        raise HTTPException(status_code=400, detail="Mesa cheia. Não há cadeiras disponíveis.")

