from fastapi import WebSocket
from typing import Dict, List, Tuple
import pprint
import asyncio
import time

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[Tuple[int, int], List[WebSocket]] = {}
        self.last_pong: Dict[WebSocket, float] = {}
        self.ping_interval = 20  # segundos
        self.timeout = 30  # segundos sem pong = kick
        asyncio.create_task(self._ping_loop())

    def receber_pong(self, websocket: WebSocket):
        self.last_pong[websocket] = time.time()


    async def _ping_loop(self):
        while True:
            await asyncio.sleep(self.ping_interval)
            
            if not self.active_connections:
                # Sem conexões ativas, pula o ciclo
                continue

            now = time.time()

            for (mid, uid), ws_list in list(self.active_connections.items()):
                for ws in list(ws_list):
                    try:
                        # Se nunca respondeu, assume que conectou agora
                        last_seen = self.last_pong.get(ws, now)
                        if now - last_seen > self.timeout:
                            print(f"[PING] WebSocket do user {uid} inativo por {now - last_seen:.1f}s, desconectando.")
                            self.disconnect(mid, uid, ws)
                            continue
                        await ws.send_json({"evento": "ping"})
                    except Exception as e:
                        print(f"[PING] Erro ao pingar user {uid}: {e}, desconectando.")
                        self.disconnect(mid, uid, ws)


    async def connect(self, mesa_id: int, user_id: int, websocket: WebSocket):
        key = (mesa_id, user_id)
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)

        # Registra o "pong" inicial
        self.last_pong[websocket] = time.time()

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

        # Limpa o last_pong também!
        if websocket in self.last_pong:
            del self.last_pong[websocket]

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

    async def send_som_jogada(self, mesa_id: int, tipo: str, jogador_id: int = None):
        """
        Envia um evento de som para todos os jogadores da mesa.
        Pode ser usado também para personalizar sons por jogador no futuro.
        """
        message = {
            "evento": "som_jogada",
            "tipo": tipo,  # "check", "call", "raise", etc.
            "jogador_id": jogador_id
        }

        for (mid, uid), ws_list in list(self.active_connections.items()):
            if mid == mesa_id:
                for ws in list(ws_list):
                    try:
                        await ws.send_json(message)
                    except Exception as e:
                        self.disconnect(mid, uid, ws)


connection_manager = ConnectionManager()
