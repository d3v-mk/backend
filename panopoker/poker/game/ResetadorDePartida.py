from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa, MesaStatus
from panopoker.websocket.manager import connection_manager
import json


class ResetadorDePartida:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db

    async def nova_rodada(self):
        from panopoker.poker.game.ControladorDePartida import ControladorDePartida

        # 0) Reset completo (reseta quem ficou e deleta quem saiu/zerou)
        await self.resetar_jogadores()

        # 1) Busca quem ainda tem saldo (estes são os ativos)
        jogadores_ativos = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .filter(JogadorNaMesa.saldo_atual > 0)
            .all()
        )

        # ⚠️ Impede da mesa voltar para aberta qnd tiver em manutencao e impede o inicio de uma nova rodada
        status_atual = MesaStatus(self.mesa.status) if isinstance(self.mesa.status, str) else self.mesa.status
        if status_atual == MesaStatus.manutencao:
            debug_print(f"[NOVA_RODADA] Mesa {self.mesa.id} está em manutenção. Abortando nova rodada.")
            return

        # 2) Se sobrar menos de 2, reabre mesa e encerra ciclo
        if len(jogadores_ativos) < 2:
            debug_print("[NOVA_RODADA] Menos de 2 jogadores ativos. Encerrando ciclo.")
            self.mesa.status = MesaStatus.aberta
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)
            self.db.commit()
            return

        # 3) Caso contrário, prepara tudo para a próxima mão
        dealer_ant = self.mesa.dealer_pos
        self.mesa.aposta_atual = 0.0
        self.mesa.pote_total = 0.0
        self.mesa.cartas_comunitarias = json.dumps({})
        self.mesa.jogador_da_vez = None
        self.mesa.estado_da_rodada = EstadoDaMesa.PRE_FLOP
        self.mesa.posicao_sb = None
        self.mesa.posicao_bb = None

        # Incrementa +1 no rodada_id
        self.mesa.rodada_id += 1



        self.mesa.dealer_pos = dealer_ant
        self.db.add(self.mesa)
        self.db.commit()
        print(f"🟡 [NOVA_RODADA] rodada_id agora é {self.mesa.rodada_id}")

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "nova_rodada"
        })

        # 5) Inicia a nova partida
        controlador = ControladorDePartida(self.mesa, self.db)
        await controlador.iniciar_partida()
        debug_print("[NOVA_RODADA] Nova partida iniciada ✅✅✅")




    async def resetar_jogadores(self):
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )

        total_postado = sum(j.aposta_atual for j in jogadores)
        
        if total_postado > 0:
            # zera as apostas antes de prosseguir
            for j in jogadores:
                j.aposta_atual = 0.0
                self.db.add(j)
            self.db.add(self.mesa)
            self.db.commit()

        for j in jogadores:
            # reseta quem tem saldo
            if j.saldo_atual > 0:
                j.aposta_atual = 0.0
                j.aposta_acumulada = 0.0
                j.foldado = False
                j.rodada_ja_agiu = False
                j.participando_da_rodada = True
                j.cartas = json.dumps([])
                self.db.add(j)
            # marca quem zerou para deletar
            else:
                j.aposta_atual = 0.0
                j.aposta_acumulada = 0.0
                j.foldado = True
                j.rodada_ja_agiu = True
                j.participando_da_rodada = False
                j.cartas = json.dumps([])
                self.db.add(j)
        self.db.commit()

        # delete mesmo quem não participa mais
        for j in jogadores:
            if j.saldo_atual <= 0 and not j.participando_da_rodada:
                debug_print(f"[RESETAR_JOGADORES] Removendo jogador {j.jogador_id} — ausente e zerado")

                # Envia aviso individual antes de remover
                await connection_manager.enviar_para_jogador(
                    mesa_id=self.mesa.id,
                    user_id=j.jogador_id,
                    message={
                        # Só avisa mesmo mas ainda nao funciona no front
                        "type": "removido_sem_saldo",
                        "mensagem": "Você ficou sem fichas e foi removido da mesa. Fale com um promotor para recarregar!"
                    }
                )

                self.db.delete(j)
        self.db.commit()  # commit da remoção!

        debug_print("[RESETAR_JOGADORES] Jogadores resetados com sucesso.")

        await connection_manager.broadcast_mesa(self.mesa.id, {
            "evento": "mesa_atualizada"
        })