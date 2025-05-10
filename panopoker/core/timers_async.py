import asyncio

# armazena futuros das mesas, não por jogador
timers_async: dict[int, asyncio.Future] = {}

# pega o loop atual assim que este módulo é importado em runtime
loop_principal = asyncio.get_event_loop()
