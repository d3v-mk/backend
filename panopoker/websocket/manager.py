from fastapi import WebSocket
from typing import Dict, List, Tuple
import pprint

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
        print(f"\n[BROADCAST_MESA] -- Enviando '{message.get('evento')}' para mesa {mesa_id}")
        print("[BROADCAST_MESA] Conexões ativas no momento:")
        pprint.pprint(self.active_connections)  # Vai printar TUDO mesmo, depois pode filtrar

        for (mid, uid), ws_list in list(self.active_connections.items()):
            if mid == mesa_id:
                print(f"  > User {uid}: {len(ws_list)} sockets")
                for ws in list(ws_list):
                    try:
                        await ws.send_json(message)
                        print(f"    - Enviado para user {uid}")
                    except Exception as e:
                        print(f"    - Falhou para user {uid}, removendo. Motivo: {e}")
                        self.disconnect(mid, uid, ws)

    async def enviar_para_jogador(self, mesa_id: int, user_id: int, message: dict):
        key = (mesa_id, user_id)
        if key in self.active_connections:
            for ws in list(self.active_connections[key]):
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(mesa_id, user_id, ws)

connection_manager = ConnectionManager()
