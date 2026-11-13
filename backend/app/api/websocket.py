"""WebSocket connection manager and endpoint."""
from typing import List, Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections and channel subscriptions."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Default subscriptions: events, alerts, simulation_status, stats
        self.subscriptions[websocket] = {"events", "alerts", "simulation_status", "stats"}

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    def subscribe(self, websocket: WebSocket, channels: List[str]):
        if websocket in self.subscriptions:
            self.subscriptions[websocket].update(channels)

    async def broadcast(self, message_type: str, data: dict):
        """Broadcast a message to subscribed clients."""
        payload = json.dumps({"type": message_type, "data": data}, default=str)
        dead_connections = []
        for connection in self.active_connections:
            # Map message type to channel
            channel = "events" if message_type == "event" else (
                "alerts" if message_type == "alert" else (
                    "stats" if message_type == "stats_update" else "simulation_status"
                )
            )
            subs = self.subscriptions.get(connection, set())
            if channel in subs or message_type in subs or not subs:
                try:
                    await connection.send_text(payload)
                except Exception:
                    dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


ws_manager = ConnectionManager()


@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
                if data.get("action") == "subscribe" and "channels" in data:
                    ws_manager.subscribe(websocket, data["channels"])
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
