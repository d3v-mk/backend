from sqlalchemy.orm import Session
from panopoker.models.mesa import Mesa
from panopoker.models.mesa import MesaStatus, JogadorNaMesa, EstadoDaMesa
from panopoker.poker.game.baralho import embaralhar, criar_baralho, distribuir_comunidade, distribuir_cartas
from fastapi import HTTPException
from itertools import combinations
import json
from panopoker.poker.game.avaliar_maos import avaliar_mao
from panopoker.core.debug import debug_print
from panopoker.usuarios.models.usuario import Usuario
from typing import Optional, List



class ControladorDePartida:
    def __init__(self, mesa: Mesa, db: Session):
        debug_print(f"[__init__] Controlador criado para mesa {mesa.id}")
        self.db = db
        self.mesa = mesa
        self.baralho = []
        self.atualizar_jogadores()
        self._mesa = mesa
        self._db = db
        
    def _preparador(self):
        from panopoker.poker.game.PreparadorDeRodada import PreparadorDeRodada
        return PreparadorDeRodada(self._mesa, self._db)


    def iniciar_partida(self):
        debug_print(f"[INICIAR_PARTIDA] Chamado iniciar_partida na mesa {self.mesa.id}")

        self.mesa.status = MesaStatus.em_jogo
        self.mesa.estado_da_rodada = EstadoDaMesa.PRE_FLOP
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"[INICIAR_PARTIDA] Status e estado atualizados para EM_JOGO e PRE_FLOP")

        self._preparador().avancar_dealer()
        debug_print(f"[INICIAR_PARTIDA] Dealer pos agora {self.mesa.dealer_pos}")

        self.atualizar_jogadores()
        debug_print(f"[INICIAR_PARTIDA] Jogadores atualizados: {[j.jogador_id for j in self.jogadores]}")

        self._preparador().definir_blinds()
        debug_print(f"[INICIAR_PARTIDA] Blinds definidos - pote: {self.mesa.pote_total}")
        self.atualizar_jogadores()  # Atualiza novamente após blinds!

        self.baralho = embaralhar(criar_baralho())
        debug_print(f"[INICIAR_PARTIDA] Baralho embaralhado, cartas restantes: {len(self.baralho)}")
        self._preparador().distribuir_cartas(self.baralho)
        self._preparador().preparar_comunitarias(self.baralho)
        debug_print(f"[INICIAR_PARTIDA] Cartas comunitárias preparadas: {self.mesa.cartas_comunitarias}")
        self._preparador().definir_primeiro_a_agir()

        debug_print(f"[INICIAR_PARTIDA] Partida iniciada na mesa {self.mesa.id}")



    def atualizar_jogadores(self):
        debug_print(f"[ATUALIZAR_JOGADORES] Atualizando lista de jogadores ativos na mesa {self.mesa.id}")
        self.jogadores = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .filter(JogadorNaMesa.participando_da_rodada == True)\
            .filter(JogadorNaMesa.foldado == False)\
            .filter(JogadorNaMesa.saldo_atual > 0)\
            .order_by(JogadorNaMesa.posicao_cadeira)\
            .all()

