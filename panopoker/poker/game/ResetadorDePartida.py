from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa, MesaStatus
import json


class ResetadorDePartida:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db

    def nova_rodada(self):
        from panopoker.poker.game.ControladorDePartida import ControladorDePartida  # 👈 lazy import aqui
        controlador = ControladorDePartida(self.mesa, self.db)
        
        jogadores_ativos = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .filter(JogadorNaMesa.saldo_atual > 0)\
            .all()

        if len(jogadores_ativos) < 2:
            debug_print("[NOVA_RODADA] Menos de 2 jogadores ativos. Encerrando ciclo.")
            self.mesa.status = MesaStatus.aberta
            self.db.add(self.mesa)
            self.db.commit()
            return

        dealer_ant = self.mesa.dealer_pos

        self.mesa.aposta_atual = 0.0
        self.mesa.pote_total = 0.0
        self.mesa.cartas_comunitarias = json.dumps({})
        self.mesa.jogador_da_vez = None
        self.mesa.estado_da_rodada = EstadoDaMesa.PRE_FLOP

        self.mesa.posicao_sb = None
        self.mesa.posicao_bb = None


        self.resetar_jogadores()

        self.mesa.dealer_pos = dealer_ant
        self.db.add(self.mesa)
        self.db.commit()

        controlador.iniciar_partida()  # ✅ Corrigido
        debug_print(f"[NOVA_RODADA] Nova partida iniciada ✅✅✅")



    def resetar_jogadores(self):
        jogadores = self.db.query(JogadorNaMesa).filter(JogadorNaMesa.mesa_id == self.mesa.id).all()
        for j in jogadores:
            if j.saldo_atual > 0:
                j.aposta_atual = 0.0
                j.aposta_acumulada = 0.0
                j.foldado = False
                j.rodada_ja_agiu = False
                j.participando_da_rodada = True
                j.cartas = json.dumps([])
                self.db.add(j)
            else:
                j.aposta_atual = 0.0
                j.aposta_acumulada = 0.0
                j.foldado = True
                j.rodada_ja_agiu = True
                j.participando_da_rodada = False
                j.cartas = json.dumps([])
                self.db.add(j)
        self.db.commit()
        debug_print(f"[RESETAR_JOGADORES] Jogadores resetados com sucesso.")