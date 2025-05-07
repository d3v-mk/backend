from panopoker.models.mesa import Mesa, JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import Session
from fastapi import HTTPException
from panopoker.core.debug import debug_print
from panopoker.models.mesa import MesaStatus
import json


class ControladorDeMesa:
    def __init__(self, mesa: Mesa, db: Session):
        self.db = db
        self.mesa = mesa

    def _controlador(self):
        from panopoker.poker.game.ControladorDePartida import ControladorDePartida
        return ControladorDePartida(self.mesa, self.db)
    

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




    def entrar_na_mesa(self, usuario: Usuario):
        jogador_existente = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .filter(JogadorNaMesa.jogador_id == usuario.id)\
            .first()

        if jogador_existente:
            raise HTTPException(status_code=400, detail="Jogador já está na mesa.")

        if usuario.saldo < self.mesa.buy_in:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para entrar na mesa.")

        # Debitar o buy-in do saldo do usuário
        usuario.saldo -= self.mesa.buy_in
        self.db.add(usuario)

        # Pegar próxima posição livre
        posicao = self._cadeira_posicao_disponivel()

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

        # 🔥 AJUSTE IMPORTANTE: Se a mesa já estiver em jogo, ele NÃO participa da rodada atual
        if self.mesa.status == MesaStatus.em_jogo:
            jogador_na_mesa.participando_da_rodada = False
        else:
            jogador_na_mesa.participando_da_rodada = True

        self.db.add(jogador_na_mesa)
        self.db.commit()

        debug_print(f"[ENTRAR_NA_MESA] Jogador {usuario.id} entrou na mesa {self.mesa.nome}")

        # Atualiza status da mesa se tiver pelo menos 2 jogadores
        jogadores = self.db.query(JogadorNaMesa)\
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)\
            .all()

        if len(jogadores) >= 2 and self.mesa.status == "aberta":
            self.db.refresh(self.mesa)
            controlador = self._controlador()
            controlador.iniciar_partida()

            








    def sair_da_mesa(self, usuario: Usuario):
        # 1) Busca o registro do jogador na mesa
        jogador = self.db.query(JogadorNaMesa) \
            .filter(JogadorNaMesa.mesa_id == self.mesa.id) \
            .filter(JogadorNaMesa.jogador_id == usuario.id) \
            .first()
        if not jogador:
            raise HTTPException(status_code=404, detail="Jogador não está na mesa.")

        # 2) Devolve o saldo atual do jogador
        saldo_para_devolver = jogador.saldo_atual
        if saldo_para_devolver > 0:
            usuario.saldo += saldo_para_devolver
            self.db.add(usuario)
            self.db.commit()

        # 3) Remove o jogador da mesa
        self.db.delete(jogador)
        self.db.commit()
        debug_print(f"[SAIR_DA_MESA] Jogador {usuario.id} saiu da mesa {self.mesa.nome} e recebeu R${saldo_para_devolver:.2f}")

        # 4) Se a mesa estava em jogo, primeiro tenta vitória automática
        if self.mesa.status == MesaStatus.em_jogo:
            ativos = self.db.query(JogadorNaMesa) \
                .filter(JogadorNaMesa.mesa_id == self.mesa.id,
                        JogadorNaMesa.participando_da_rodada == True,
                        JogadorNaMesa.foldado == False,
                        JogadorNaMesa.saldo_atual > 0) \
                .all()
            
        if self.verificar_vitoria_automatica():
            return

        # 5) Se sobrar menos de 2 sentados, mesa volta a 'aberta'
        jogadores_restantes = self.db.query(JogadorNaMesa) \
            .filter(JogadorNaMesa.mesa_id == self.mesa.id) \
            .count()
        if jogadores_restantes < 2:
            self.mesa.status = MesaStatus.aberta
            self.db.add(self.mesa)
            self.db.commit()
            debug_print(f"[SAIR_DA_MESA] Mesa {self.mesa.id} voltou para 'aberta' por falta de jogadores.")
            return

        # 6) Se quem saiu era da vez, limpa e avança para o próximo
        if self.mesa.jogador_da_vez == usuario.id:
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)
            self.db.commit()
            debug_print(f"[SAIR_DA_MESA] Jogador {usuario.id} era da vez — limpando vez.")
            controlador_temp = self._controlador()
            controlador_temp.avancar_vez()









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

