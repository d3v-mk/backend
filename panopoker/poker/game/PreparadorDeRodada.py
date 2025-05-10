from sqlalchemy.orm import Session
from panopoker.core.debug import debug_print
from panopoker.poker.models.mesa import Mesa, JogadorNaMesa, EstadoDaMesa
from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy import or_
import json


class PreparadorDeRodada:
    def __init__(self, mesa: Mesa, db: Session):
        self.mesa = mesa
        self.db = db


    def avancar_dealer(self):
        debug_print("🔁========== Início AVANCAR_DEALER ==========")
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(JogadorNaMesa.mesa_id == self.mesa.id)
            .order_by(JogadorNaMesa.posicao_cadeira)
            .all()
        )
        if not jogadores:
            raise HTTPException(status_code=400, detail="Não há jogadores suficientes para avançar o dealer.")

        posicoes = [j.posicao_cadeira for j in jogadores]
        debug_print(f"🔍 Posições ocupadas: {posicoes}")

        if self.mesa.dealer_pos is None or self.mesa.dealer_pos not in posicoes:
            proxima_pos = posicoes[0]
            debug_print(f"⚠️ Dealer indefinido. Setando primeiro: {proxima_pos}")
        else:
            proxima_pos = next((p for p in posicoes if p > self.mesa.dealer_pos), posicoes[0])
            debug_print(f"➡️ Dealer avançado de {self.mesa.dealer_pos} para {proxima_pos}")

        self.mesa.dealer_pos = proxima_pos
        self.db.add(self.mesa)
        self.db.commit()




    def definir_blinds(self):
        debug_print("🔁========== Início DEFINIR_BLINDS ==========")
        # pega todos os que vão participar (saldo>0)
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.saldo_atual > 0
            )
            .order_by(JogadorNaMesa.posicao_cadeira)
            .all()
        )
        if len(jogadores) < 2:
            raise HTTPException(status_code=400, detail="Não há jogadores suficientes para definir blinds.")

        # --- RESETA rodada_ja_agiu para todos antes de postar blinds ---
        for j in jogadores:
            j.rodada_ja_agiu = False
            self.db.add(j)
        self.db.commit()

        posicoes = [j.posicao_cadeira for j in jogadores]
        mp = {j.posicao_cadeira: j for j in jogadores}
        dealer_pos = self.mesa.dealer_pos

        # heads-up ou multi-jogadores
        if len(jogadores) == 2:
            sb_pos = dealer_pos
            bb_pos = next(p for p in posicoes if p != dealer_pos)
        else:
            sb_pos = next((p for p in posicoes if p > dealer_pos), posicoes[0])
            bb_pos = next((p for p in posicoes if p > sb_pos), posicoes[0])

        sb = mp[sb_pos]
        bb = mp[bb_pos]
        debug_print(f"🎯 SB: jogador {sb.jogador_id} em pos {sb_pos}, BB: jogador {bb.jogador_id} em pos {bb_pos}")

        # valor real dos blinds (pode ser menor que o blind se faltar saldo)
        sb_aposta = min(self.mesa.small_blind, sb.saldo_atual)
        bb_aposta = min(self.mesa.big_blind, bb.saldo_atual)

        # desconta do saldo
        sb.saldo_atual -= sb_aposta
        bb.saldo_atual -= bb_aposta

        # **acumula os blinds no total investido**
        sb.aposta_acumulada += sb_aposta
        bb.aposta_acumulada += bb_aposta

        # se postou todo o stack, marca como all-in (já agiu)
        if sb.saldo_atual <= 0:
            sb.rodada_ja_agiu = True
            debug_print(f"[BLINDS] Jogador SB {sb.jogador_id} all-in no blind")
        else:
            sb.rodada_ja_agiu = False

        if bb.saldo_atual <= 0:
            bb.rodada_ja_agiu = True
            debug_print(f"[BLINDS] Jogador BB {bb.jogador_id} all-in no blind")
        else:
            bb.rodada_ja_agiu = False

        # registra aposta atual e zera flag de ação
        sb.aposta_atual = sb_aposta
        bb.aposta_atual = bb_aposta

        # atualiza mesa
        self.mesa.aposta_atual = bb_aposta
        self.mesa.posicao_sb = sb_pos
        self.mesa.posicao_bb = bb_pos

        # persiste
        self.db.add_all([sb, bb, self.mesa])
        self.db.commit()
        debug_print(f"✅ Blinds definidos: SB={sb_aposta}, BB={bb_aposta}")




    def distribuir_cartas(self, baralho: List[str]):
        debug_print("🔁========== Início DISTRIBUIR_CARTAS ==========")
        jogadores = (
            self.db.query(JogadorNaMesa)
              .filter(
                  JogadorNaMesa.mesa_id == self.mesa.id,
                  JogadorNaMesa.participando_da_rodada == True,
                  JogadorNaMesa.foldado == False
              )
              .order_by(JogadorNaMesa.posicao_cadeira)
              .all()
        )

        for j in jogadores:
            if len(baralho) < 2:
                raise HTTPException(status_code=400, detail="Baralho insuficiente para distribuir cartas.")

            cartas = []
            for _ in range(2):
                raw = baralho.pop()       # ex: "8E" ou "10P"
                s = str(raw)
                # valida mínimo de 2 chars (valor + naipe)
                if len(s) < 2:
                    raise HTTPException(400, detail=f"Carta malformada no baralho: {raw!r}")
                cartas.append(s)

            j.cartas = json.dumps(cartas)
            debug_print(f"🃏 Jogador {j.jogador_id} recebeu: {cartas}")
            self.db.add(j)

        self.db.commit()




    def preparar_comunitarias(self, baralho: List[str]):
        if len(baralho) < 5:
            raise HTTPException(status_code=400, detail="Baralho insuficiente para comunitárias.")

        def valida(raw):
            s = str(raw)
            if len(s) < 2:
                raise HTTPException(400, detail=f"Carta malformada no baralho: {raw!r}")
            return s

        flop = [valida(baralho.pop()) for _ in range(3)]
        turn = valida(baralho.pop())
        river = valida(baralho.pop())

        self.mesa.cartas_comunitarias = {"flop": flop, "turn": turn, "river": river}
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"🌐 Comunitárias definidas: Flop={flop}, Turn={turn}, River={river}")




    def definir_primeiro_a_agir(self):
        debug_print("🔁========== Início DEFINIR_PRIMEIRO_A_AGIR ==========")
        # agora incluímos também quem está all-in (saldo 0 mas aposta > 0)
        jogadores = (
            self.db.query(JogadorNaMesa)
            .filter(
                JogadorNaMesa.mesa_id == self.mesa.id,
                JogadorNaMesa.participando_da_rodada == True,
                JogadorNaMesa.foldado == False,
                or_(
                    JogadorNaMesa.saldo_atual > 0,
                    JogadorNaMesa.aposta_atual > 0
                )
            )
            .order_by(JogadorNaMesa.posicao_cadeira)
            .all()
        )
        if not jogadores:
            raise HTTPException(status_code=400, detail="Não há jogadores ativos para definir o primeiro a agir.")

        posicoes = [j.posicao_cadeira for j in jogadores]
        mp = {j.posicao_cadeira: j for j in jogadores}
        primeiro_pos = None

        # heads-up
        if len(jogadores) == 2:
            dealer_pos = self.mesa.dealer_pos
            if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP:
                primeiro_pos = dealer_pos
                debug_print(f"🌀 HEADS-UP PRE-FLOP: Dealer {dealer_pos} age primeiro")
            else:
                nao_dealer = [p for p in posicoes if p != dealer_pos][0]
                primeiro_pos = nao_dealer
                debug_print(f"🌀 HEADS-UP POS-FLOP: pos {primeiro_pos} age primeiro")
        else:
            # multi-jogadores
            if self.mesa.estado_da_rodada == EstadoDaMesa.PRE_FLOP:
                bb_pos = next(
                    (j.posicao_cadeira for j in jogadores
                     if abs(j.aposta_atual - self.mesa.aposta_atual) < 1e-3),
                    None
                )
                primeiro_pos = next((p for p in posicoes if p > bb_pos), posicoes[0])
                debug_print(f"🔥 Multi-jog Pre-Flop: primeiro é pos {primeiro_pos}")
            else:
                dealer_pos = self.mesa.dealer_pos if self.mesa.dealer_pos in posicoes else posicoes[-1]
                idx = (posicoes.index(dealer_pos) + 1) % len(posicoes)
                primeiro_pos = posicoes[idx]
                debug_print(f"🔥 Multi-jog Pós-Flop: primeiro é pos {primeiro_pos}")

        jog = mp.get(primeiro_pos)
        if not jog:
            # caso algo estranho aconteça, repassa a vez
            debug_print(f"❌ Posição {primeiro_pos} inválida, repassando vez")
            from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada
            GerenciadorDeRodada(self.mesa, self.db).avancar_vez()
            return

        self.mesa.jogador_da_vez = jog.jogador_id
        self.db.add(self.mesa)
        self.db.commit()
        debug_print(f"✅ Primeiro a agir definido: jogador {jog.jogador_id} (pos {primeiro_pos})")

        from panopoker.poker.game.GerenciadorDeRodada import GerenciadorDeRodada
        GerenciadorDeRodada(self.mesa, self.db).iniciar_timer_vez(jog.jogador_id)
        debug_print(f"[DEFINIR_PRIMEIRO_A_AGIR]⏳ Iniciando timer async para jogador {self.mesa.jogador_da_vez}.")