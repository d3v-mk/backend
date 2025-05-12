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
        from panopoker.poker.game.GerenciadorDeRodada import marcar_como_ausente
        # Converte e debug
        try:
            user_id = int(usuario.id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="ID de usuário inválido.")
        debug_print(f"[SAIR_DA_MESA] Tentando remover jogador {user_id} da mesa {self.mesa.id}")

        # Lista todos antes (para debug)
        todos = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .all()
        )
        debug_print(f"[SAIR_DA_MESA] IDs na mesa: {[j.jogador_id for j in todos]}")

        # Busca o jogador pelo par (mesa, jogador)
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

        # 4) Move aposta_atual direto pro pote da mesa
        if jogador.aposta_atual > 0:
            valor = jogador.aposta_atual
            debug_print(f"[SAIR_DA_MESA] Movendo R${valor:.2f} do jogador {user_id} direto para pote_total")
            # acumula no pote
            self.mesa.pote_total = (self.mesa.pote_total or 0) + valor
            # zera a aposta dele
            jogador.aposta_atual = 0
            # persiste as duas mudanças
            self.db.add_all([self.mesa, jogador])
            self.db.commit()

        # Marca como ausente/fold na rodada
        marcar_como_ausente(jogador)

        # Devolve saldo_atual, se houver
        if jogador.saldo_atual > 0:
            debug_print(f"[SAIR_DA_MESA] Devolvendo R${jogador.saldo_atual:.2f} p/ usuário {user_id}")
            usuario.saldo += jogador.saldo_atual
            jogador.saldo_atual = 0
            self.db.add_all([usuario, jogador])

        self.db.commit()

        # Filtra apenas jogadores ativos na mão (não foldados)
        ativos = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True
            )
            .all()
        )

        # Se sobrou <= 1 ativo, encerrar ronda
        if len(ativos) <= 1:
            self._gerenciador().cancelar_timer()

            # Vitória automática
            if len(ativos) == 1 and self.mesa.status == MesaStatus.em_jogo:
                vencedor = ativos[0]
                debug_print(f"[SAIR_DA_MESA] Vitória automática para jogador {vencedor.jogador_id}")
                self._distribuidor().atualizar_pote_total()
                self._distribuidor().distribuir_pote(vencedor)
            
            # Nova rodada ou reabrir mesa
            self._resetador().nova_rodada()

            # Se nenhum ativo, reabrir mesa
            if not ativos:
                self.mesa.status = MesaStatus.aberta
                self.mesa.jogador_da_vez = None
                self.db.add(self.mesa)
                self.db.commit()
                debug_print(f"[SAIR_DA_MESA] Mesa {self.mesa.id} voltou para 'aberta' por falta de jogadores.")
            return

        # Se era a vez dele, avança para o próximo ativo
        if self.mesa.jogador_da_vez == user_id:
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

