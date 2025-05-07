import random

# Definindo os naipes e valores
naipes = ['E', 'C', 'O', 'P']
valores = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Função para criar um baralho padrão de 52 cartas
def criar_baralho():
    baralho = [f"{valor}{naipe}" for naipe in naipes for valor in valores]
    return baralho

# Embaralhar o baralho
def embaralhar(baralho):
    random.shuffle(baralho)
    return baralho

# Distribuir 2 cartas para cada jogador
def distribuir_cartas(jogadores_ids, baralho):
    mao_jogadores = {}
    for jogador_id in jogadores_ids:
        mao_jogadores[jogador_id] = [baralho.pop(), baralho.pop()]
    return mao_jogadores, baralho  # Retorna o baralho atualizado

# Flop, turn, river (simulando a ordem do Texas Hold'em)
def distribuir_comunidade(baralho):
    flop = [baralho.pop() for _ in range(3)]  # 3 cartas do flop
    turn = baralho.pop()  # 1 carta do turn
    river = baralho.pop()  # 1 carta do river
    return flop, turn, river, baralho  # Retorna o baralho atualizado