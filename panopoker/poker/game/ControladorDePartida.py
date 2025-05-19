from sqlalchemy.orm import Session
from panopoker.poker.models.mesa import Mesa
from panopoker.poker.models.mesa import MesaStatus, JogadorNaMesa, EstadoDaMesa
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
        self.db = db
        self.mesa = mesa
        self.baralho = []
        self.atualizar_jogadores()
        
    def _preparador(self):
        from panopoker.poker.game.PreparadorDeRodada import PreparadorDeRodada
        return PreparadorDeRodada(self.mesa, self.db)


    async def iniciar_partida(self):

        self.mesa.status = MesaStatus.em_jogo
        self.mesa.estado_da_rodada = EstadoDaMesa.PRE_FLOP
        self.db.add(self.mesa)
        self.db.commit()


        self._preparador().avancar_dealer()

        self.atualizar_jogadores()

        self._preparador().definir_blinds()
        
        self.atualizar_jogadores()  # Atualiza novamente após blinds!

        self.baralho = embaralhar(criar_baralho())

        self._preparador().distribuir_cartas(self.baralho)

        self._preparador().preparar_comunitarias(self.baralho)

        self._preparador().definir_primeiro_a_agir()

        debug_print(f"[INICIAR_PARTIDA] Partida iniciada na mesa {self.mesa.id}")



    def atualizar_jogadores(self):
        self.jogadores = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .filter(JogadorNaMesa.participando_da_rodada == True)\
            .filter(JogadorNaMesa.foldado == False)\
            .filter(JogadorNaMesa.saldo_atual > 0)\
            .order_by(JogadorNaMesa.posicao_cadeira)\
            .all()

