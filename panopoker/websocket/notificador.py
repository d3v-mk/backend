from panopoker.websocket.manager import connection_manager

async def notificar_mesa(mesa_id: int, evento: str, dados: dict):
    await connection_manager.broadcast_mesa(mesa_id, {
        "evento": evento,
        "dados": dados
    })
