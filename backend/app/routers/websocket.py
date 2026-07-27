"""
NEXUS — WebSocket Router
========================
WebSocket endpoints for real-time API updates and notifications.
"""

import logging
import json
import uuid
import asyncio
from typing import Optional, Set
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from app.core.api_gateway import (
    api_gateway,
    APIEventType,
    ConnectionManager
)
from app.engines.control_tower import ControlTowerEngine

logger_ws = logging.getLogger("nexus.websocket")

router = APIRouter(prefix="/ws", tags=["websocket"])

# Control Tower engine instance
control_tower_engine = ControlTowerEngine()


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: dict
    timestamp: Optional[str] = None


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    subscriptions: Optional[str] = Query(None)
):
    """
    Main WebSocket endpoint for real-time updates.
    
    Query Parameters:
    - client_id: Optional client identifier (auto-generated if not provided)
    - subscriptions: Comma-separated list of event types to subscribe to
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client_{uuid.uuid4().hex[:8]}"
    
    # Parse subscriptions
    event_types = []
    if subscriptions:
        try:
            requested_subscriptions = subscriptions.split(",")
            event_types = [APIEventType(s.strip()) for s in requested_subscriptions if s.strip()]
        except ValueError as e:
            logger_ws.error(f"Invalid subscription types: {e}")
            event_types = list(APIEventType)  # Default to all
    else:
        event_types = list(APIEventType)  # Default to all
    
    # Connect client
    connection_result = await api_gateway.connection_manager.connect(
        websocket=websocket,
        client_id=client_id,
        metadata={"connected_at": datetime.now(timezone.utc).isoformat()}
    )
    
    if "error" in connection_result:
        await websocket.close(code=4000, reason=connection_result["error"])
        return
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connection_established",
        "data": connection_result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Update subscriptions if specific ones were requested
    if event_types != list(APIEventType):
        await api_gateway.connection_manager.subscribe(client_id, event_types)
    
    try:
        # Listen for incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type", "unknown")
            
            if message_type == "ping":
                # Respond to ping with pong
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": datetime.now(timezone.utc).isoformat()},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            elif message_type == "subscribe":
                # Handle subscription changes
                new_subscriptions = message.get("data", {}).get("subscriptions", [])
                try:
                    event_types_to_subscribe = [APIEventType(s) for s in new_subscriptions]
                    result = await api_gateway.connection_manager.subscribe(
                        client_id, event_types_to_subscribe
                    )
                    await websocket.send_json({
                        "type": "subscription_updated",
                        "data": result,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except ValueError as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"error": f"Invalid subscription types: {e}"},
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            elif message_type == "unsubscribe":
                # Handle unsubscription
                subscriptions_to_remove = message.get("data", {}).get("subscriptions", [])
                try:
                    event_types_to_unsubscribe = [APIEventType(s) for s in subscriptions_to_remove]
                    result = await api_gateway.connection_manager.unsubscribe(
                        client_id, event_types_to_unsubscribe
                    )
                    await websocket.send_json({
                        "type": "subscription_updated",
                        "data": result,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except ValueError as e:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"error": f"Invalid subscription types: {e}"},
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            elif message_type == "get_status":
                # Send current connection status
                stats = api_gateway.connection_manager.get_connection_stats()
                await websocket.send_json({
                    "type": "status",
                    "data": {
                        "client_id": client_id,
                        "subscriptions": [e.value for e in api_gateway.connection_manager.subscriptions.get(client_id, set())],
                        "server_stats": stats
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "data": {"error": f"Unknown message type: {message_type}"},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        # Handle disconnection
        disconnect_result = await api_gateway.connection_manager.disconnect(client_id)
        logger_ws.info(f"Client {client_id} disconnected: {disconnect_result}")
    
    except Exception as e:
        logger_ws.error(f"WebSocket error for client {client_id}: {e}")
        await api_gateway.connection_manager.disconnect(client_id)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return api_gateway.connection_manager.get_connection_stats()


@router.post("/broadcast")
async def broadcast_event(message: WebSocketMessage):
    """
    Manually broadcast an event to all connected WebSocket clients.
    This is primarily for testing and administrative purposes.
    """
    try:
        event_type = APIEventType(message.type)
        result = await api_gateway.broadcast_event(
            event_type=event_type,
            data=message.data,
            source="manual_broadcast"
        )
        return result
    except ValueError:
        return {"error": f"Invalid event type: {message.type}"}
    except Exception as e:
        logger_ws.error(f"Error broadcasting event: {e}")
        return {"error": str(e)}


@router.websocket("/control-tower")
async def control_tower_websocket(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time Control Tower data streaming.
    Provides live alerts, metrics, and monitoring updates.
    
    Query Parameters:
    - client_id: Optional client identifier (auto-generated if not provided)
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = f"ct_client_{uuid.uuid4().hex[:8]}"
    
    # Initialize control tower if needed
    if not control_tower_engine._initialised:
        control_tower_engine.initialize()
    
    # Accept connection
    await websocket.accept()
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "control_tower_connected",
        "data": {
            "client_id": client_id,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "message": "Connected to Control Tower real-time stream"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        # Send initial data
        active_alerts = control_tower_engine.get_active_alerts()
        await websocket.send_json({
            "type": "initial_alerts",
            "data": active_alerts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Simulate real-time updates (in production, this would be event-driven)
        update_count = 0
        
        while True:
            # Wait for 30 seconds between updates
            await asyncio.sleep(30)
            update_count += 1
            
            # Generate simulated updates
            if update_count % 2 == 0:
                # Send alert updates
                alert_update = {
                    "type": "alert_update",
                    "data": {
                        "update_type": "refresh",
                        "active_alerts": len(control_tower_engine.active_alerts),
                        "recent_alerts": list(control_tower_engine.alert_history[-5:]) if control_tower_engine.alert_history else []
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await websocket.send_json(alert_update)
            
            if update_count % 3 == 0:
                # Send metric updates
                metric_update = {
                    "type": "metric_update",
                    "data": {
                        "system_health": 95.0,
                        "active_incidents": 0,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await websocket.send_json(metric_update)
            
            # Send keepalive
            await websocket.send_json({
                "type": "keepalive",
                "data": {"sequence": update_count},
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    except WebSocketDisconnect:
        logger_ws.info(f"Control Tower client {client_id} disconnected")
    
    except Exception as e:
        logger_ws.error(f"Control Tower WebSocket error for client {client_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "data": {"error": str(e)},
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except:
            pass
        finally:
            await websocket.close()