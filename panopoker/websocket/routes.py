from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from panopoker.websocket.manager import connection_manager

router = APIRouter()

@router.websocket("/ws/mesa/{mesa_id}")
async def websocket_mesa(websocket: WebSocket, mesa_id: int):
    await connection_manager.connect(mesa_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # segura a conexão
    except WebSocketDisconnect:
        connection_manager.disconnect(mesa_id, websocket)
