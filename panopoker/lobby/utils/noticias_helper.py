from typing import List, Tuple
from panopoker.poker.models.mesa import JogadorNaMesa

def registrar_evento(mensagem, db, mesa_id=None, usuario_id=None, tipo="evento", admin=False):
    from panopoker.lobby.models.noticias import Noticia  # Importa aqui pra evitar circular import

    noticia = Noticia(
        mensagem=mensagem,
        tipo="admin" if admin else tipo,
        mesa_id=mesa_id,
        usuario_id=usuario_id
    )
    db.add(noticia)
    db.commit()
    db.refresh(noticia)  # Se quiser o objeto atualizado
    return noticia



def identificar_vencedores(resultados: List[Tuple[JogadorNaMesa, Tuple[int, List[int]]]]) -> List[JogadorNaMesa]:
    resultados.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)
    melhor = resultados[0][1]
    return [j for j, r in resultados if r == melhor]



def registrar_eventos_showdown(participantes, cartas_mesa, side_pots, mesa, db):
    import json
    from panopoker.poker.game.avaliar_maos import avaliar_mao

    # map rank → nome da conquista (Só Sequência pra cima)
    conquistas_rank = {
        10: "Royal Flush",
        9: "Straight Flush",
        8: "Quadra",
        7: "Full House",
        6: "Flush",
        5: "Sequência",
        #4: "Trinca",
        #3: "Dois Pares",
        #2: "Par",
        #1: "Carta Alta"
    }

    for amount, grupo in side_pots:
        # pulando todos os pots pequenos
        if amount <= 0.01:     # Ajustar com o tempo no MVP vamo exibir todos
            continue

        # monta lista (jogador, (rank_num, detalhes))
        resultados = []
        for j in grupo:
            hole = json.loads(j.cartas) if isinstance(j.cartas, str) else j.cartas
            resultados.append((j, avaliar_mao(hole + cartas_mesa)))
        winners = identificar_vencedores(resultados)
        ganho = amount / len(winners) if winners else 0

        for j, (rank_num, _) in resultados:
            if j not in winners:
                continue

            nome = getattr(j.jogador, "nome", f"ID {j.jogador_id}")
            if rank_num in conquistas_rank:
                conquista = conquistas_rank[rank_num]
                registrar_evento(
                    mensagem=(
                        f"{nome}, {conquista}! na {mesa.nome} "
                        f"pote: {ganho:.2f} 🔥"
                    ),
                    db=db,
                    mesa_id=mesa.id,
                    usuario_id=j.jogador_id,
                    tipo="conquista"
                )
            else:
                registrar_evento(
                    mensagem=(
                        f"{nome} ganhou {ganho:.2f} fichas na {mesa.nome}!"
                    ),
                    db=db,
                    mesa_id=mesa.id,
                    usuario_id=j.jogador_id,
                    tipo="evento"
                )



# -------- USO PARA ADMIN --------
# Sepa q isso ta inutil, ver depoois
def registrar_mensagem_admin(mensagem, db, mesa_id=None):
    return registrar_evento(
        mensagem=mensagem,
        db=db,
        mesa_id=mesa_id,
        usuario_id=None,
        tipo="admin",
        admin=True
    )
