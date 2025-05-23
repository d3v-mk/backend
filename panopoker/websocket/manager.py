from fastapi import WebSocket
from typing import Dict, List, Tuple

class ConnectionManager:
    def __init__(self):
        # Agora permite *várias* conexões por (mesa_id, user_id)
        self.active_connections: Dict[Tuple[int, int], List[WebSocket]] = {}

    async def connect(self, mesa_id: int, user_id: int, websocket: WebSocket):
        key = (mesa_id, user_id)
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)

    def disconnect(self, mesa_id: int, user_id: int, websocket: WebSocket):
        key = (mesa_id, user_id)
        if key in self.active_connections:
            # Remove só esse websocket, mantém os outros devices!
            try:
                self.active_connections[key].remove(websocket)
            except ValueError:
                pass
            # Se não sobrou nenhum, tira a key do dicionário
            if not self.active_connections[key]:
                del self.active_connections[key]

    async def broadcast_mesa(self, mesa_id: int, message: dict):
        # Manda para todos os sockets dessa mesa (de todos os users)
        for (mid, uid), ws_list in list(self.active_connections.items()):
            if mid == mesa_id:
                for ws in list(ws_list):  # copia pra não bugar se remover
                    try:
                        await ws.send_json(message)
                    except Exception:
                        # Remove só essa conexão zoada
                        self.disconnect(mid, uid, ws)

connection_manager = ConnectionManager()
