from fastapi import WebSocket
from typing import Dict, List
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, mesa_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(mesa_id, []).append(websocket)

    def disconnect(self, mesa_id: int, websocket: WebSocket):
        self.active_connections[mesa_id].remove(websocket)

    async def broadcast_mesa(self, mesa_id: int, message: dict):
        connections = self.active_connections.get(mesa_id, [])
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Se o socket tiver zoado, remove da lista
                self.disconnect(mesa_id, connection)

connection_manager = ConnectionManager()
