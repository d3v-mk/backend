from sqlalchemy import or_, func, desc

from panopoker.poker.models.mesa import Mesa  # importa a classe certa lá em cima

def matchmaking_helper(db, buy_in):
    print(f"[HELPER] Procurando mesa para buy_in={buy_in}")

    try:
        mesa_com_jogador = db.query(Mesa)\
            .join(Mesa.jogadores)\
            .filter(Mesa.buy_in == buy_in)\
            .filter(or_(Mesa.status == "aberta", Mesa.status == "em_jogo"))\
            .group_by(Mesa.id)\
            .having(func.count(Mesa.jogadores).between(1, 5))\
            .order_by(desc(func.count(Mesa.jogadores)))\
            .first()
        
        print(f"[HELPER] Mesa com 1-5 jogadores: {mesa_com_jogador}")

        if mesa_com_jogador:
            print(f"[HELPER] Encontrou mesa com jogadores: {mesa_com_jogador.id}")
            return mesa_com_jogador

        mesas_vazias = db.query(Mesa)\
            .filter(Mesa.buy_in == buy_in)\
            .filter(Mesa.status == "aberta")\
            .all()

        print(f"[HELPER] Mesas abertas disponíveis: {[m.id for m in mesas_vazias]}")

        for mesa in mesas_vazias:
            jogadores_na_mesa = len(mesa.jogadores)
            print(f"[HELPER] Mesa id={mesa.id} tem {jogadores_na_mesa} jogadores")
            if jogadores_na_mesa < 6:
                print(f"[HELPER] Encontrou mesa vazia com vaga: {mesa.id}")
                return mesa

        print("[HELPER] Nenhuma mesa encontrada.")
        return None

    except Exception as e:
        print(f"[HELPER] ERRO GERAL: {e}")
        return None