from panopoker.poker.models.mesa import Mesa, JogadorNaMesa
from panopoker.usuarios.models.usuario import Usuario
from panopoker.core.security import Session
from fastapi import HTTPException
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import MesaStatus
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
            debug_print(f"[SAIR_DA_MESA] Jogador {usuario.id} saiu da mesa {self.mesa.nome} e recebeu R${saldo_para_devolver:.2f}")

        # 2.1) Coloca a aposta_atual do jogador que saiu no side pote
        if jogador.aposta_atual > 0:
            debug_print(f"[SAIR_DA_MESA] Adicionando aposta_atual R${jogador.aposta_atual:.2f} para aposta_acumulada antes de sair")
            jogador.aposta_acumulada += jogador.aposta_atual
            jogador.aposta_atual = 0
            self.db.add(jogador)
            self.db.commit()

        # 3) Remove o jogador da mesa
        self.db.delete(jogador)
        self.db.commit()


        # 4) Verifica quantos jogadores restaram
        jogadores_restantes = self.db.query(JogadorNaMesa) \
            .filter(JogadorNaMesa.mesa_id == self.mesa.id) \
            .all()

        if len(jogadores_restantes) < 2:
            self._gerenciador().cancelar_timer()

            # ✅ VERIFICA SE HÁ UM VENCEDOR ANTES DE FECHAR A MESA
            if len(jogadores_restantes) == 1 and self.mesa.status == MesaStatus.em_jogo:
                debug_print(f"[SAIR_DA_MESA] Vitória automática para jogador {jogadores_restantes[0].jogador_id}")
                self._distribuidor().atualizar_pote_total()
                self._distribuidor().distribuir_pote(jogadores_restantes[0])
                self._resetador().nova_rodada()
                return

            # ⛔ Se não tiver vencedor, aí sim volta pra aberta
            self.mesa.status = MesaStatus.aberta
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)

            if jogadores_restantes:
                unico = jogadores_restantes[0]
                if unico.aposta_atual > 0:
                    debug_print(f"[SAIR_DA_MESA] Devolvendo aposta R${unico.aposta_atual:.2f} para jogador {unico.jogador_id}")
                    unico.saldo_atual += unico.aposta_atual
                    unico.aposta_atual = 0
                    self.db.add(unico)

            self.db.commit()
            debug_print(f"[SAIR_DA_MESA] Mesa {self.mesa.id} voltou para 'aberta' por falta de jogadores.")
            return


        # 5) Se quem saiu era da vez, limpa e avança
        if self.mesa.jogador_da_vez == usuario.id:
            self.mesa.jogador_da_vez = None
            self.db.add(self.mesa)
            self.db.commit()
            self._gerenciador().avancar_vez()










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

