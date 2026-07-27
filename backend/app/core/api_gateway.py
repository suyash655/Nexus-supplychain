"""
NEXUS — API Gateway with GraphQL and WebSocket Support
======================================================
Advanced API gateway with GraphQL query interface, WebSocket support
for real-time updates, and comprehensive API management.
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from enum import Enum
import uuid
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from fastapi import WebSocket, WebSocketDisconnect
    from fastapi.api_docs import get_openapi
except ImportError:
    # Handle cases where FastAPI might not be fully available
    WebSocket = None
    WebSocketDisconnect = Exception

logger_gw = logging.getLogger("nexus.api_gateway")


class APIEventType(Enum):
    """Types of API events for WebSocket broadcasting."""
    DEMAND_UPDATE = "demand_update"
    INVENTORY_CHANGE = "inventory_change"
    RISK_ALERT = "risk_alert"
    SUPPLIER_STATUS = "supplier_status"
    ANALYSIS_COMPLETE = "analysis_complete"
    SCENARIO_UPDATE = "scenario_update"
    SYSTEM_STATUS = "system_status"


@dataclass
class APIEvent:
    """Represents an API event for WebSocket broadcasting."""
    event_type: APIEventType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = "system"


class ConnectionManager:
    """
    Manages WebSocket connections for real-time API updates.
    Handles connection lifecycle, message broadcasting, and subscription management.
    """

    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connection subscriptions (connection_id -> set of event types)
        self.subscriptions: Dict[str, Set[APIEventType]] = defaultdict(set)
        
        # Event type to connections mapping (for efficient broadcasting)
        self.event_subscribers: Dict[APIEventType, Set[str]] = defaultdict(set)
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            metadata: Optional connection metadata
        """
        await websocket.accept()
        
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = metadata or {}
        
        # Subscribe to all events by default
        default_subscriptions = set(APIEventType)
        self.subscriptions[client_id] = default_subscriptions
        
        for event_type in default_subscriptions:
            self.event_subscribers[event_type].add(client_id)
        
        logger_gw.info(f"WebSocket client connected: {client_id}")
        
        return {
            "status": "connected",
            "client_id": client_id,
            "subscribed_events": [e.value for e in default_subscriptions],
            "connected_at": datetime.now(timezone.utc).isoformat()
        }

    async def disconnect(self, client_id: str) -> Dict[str, Any]:
        """
        Disconnect a WebSocket client.
        
        Args:
            client_id: Client identifier to disconnect
        """
        if client_id in self.active_connections:
            # Remove from all subscriber lists
            for event_type in self.subscriptions[client_id]:
                self.event_subscribers[event_type].discard(client_id)
            
            # Clean up
            del self.active_connections[client_id]
            del self.subscriptions[client_id]
            del self.connection_metadata[client_id]
            
            logger_gw.info(f"WebSocket client disconnected: {client_id}")
            
            return {
                "status": "disconnected",
                "client_id": client_id,
                "disconnected_at": datetime.now(timezone.utc).isoformat()
            }
        
        return {"error": "Client not found"}

    async def subscribe(self, client_id: str, event_types: List[APIEventType]) -> Dict[str, Any]:
        """
        Subscribe a client to specific event types.
        
        Args:
            client_id: Client identifier
            event_types: List of event types to subscribe to
        """
        if client_id not in self.active_connections:
            return {"error": "Client not connected"}
        
        # Update subscriptions
        for event_type in event_types:
            self.subscriptions[client_id].add(event_type)
            self.event_subscribers[event_type].add(client_id)
        
        logger_gw.info(f"Client {client_id} subscribed to {[e.value for e in event_types]}")
        
        return {
            "status": "subscribed",
            "client_id": client_id,
            "subscribed_events": [e.value for e in event_types],
            "all_subscriptions": [e.value for e in self.subscriptions[client_id]]
        }

    async def unsubscribe(self, client_id: str, event_types: List[APIEventType]) -> Dict[str, Any]:
        """
        Unsubscribe a client from specific event types.
        
        Args:
            client_id: Client identifier
            event_types: List of event types to unsubscribe from
        """
        if client_id not in self.active_connections:
            return {"error": "Client not connected"}
        
        # Update subscriptions
        for event_type in event_types:
            self.subscriptions[client_id].discard(event_type)
            self.event_subscribers[event_type].discard(client_id)
        
        logger_gw.info(f"Client {client_id} unsubscribed from {[e.value for e in event_types]}")
        
        return {
            "status": "unsubscribed",
            "client_id": client_id,
            "unsubscribed_events": [e.value for e in event_types],
            "remaining_subscriptions": [e.value for e in self.subscriptions[client_id]]
        }

    async def broadcast(self, event: APIEvent) -> Dict[str, Any]:
        """
        Broadcast an event to all subscribed clients.
        
        Args:
            event: API event to broadcast
        """
        subscribers = self.event_subscribers.get(event.event_type, set())
        successful_sends = 0
        failed_sends = 0
        
        message = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "data": event.data,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source
        }
        
        for client_id in subscribers:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_json(message)
                    successful_sends += 1
                except Exception as e:
                    logger_gw.error(f"Error sending to client {client_id}: {e}")
                    failed_sends += 1
                    # Disconnect failed client
                    await self.disconnect(client_id)
        
        logger_gw.info(f"Broadcast event {event.event_type.value} to {successful_sends} clients")
        
        return {
            "status": "broadcast",
            "event_type": event.event_type.value,
            "event_id": event.event_id,
            "subscribers": len(subscribers),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends
        }

    async def send_personal_message(self, client_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a specific client.
        
        Args:
            client_id: Client identifier
            message: Message to send
        """
        if client_id not in self.active_connections:
            return {"error": "Client not connected"}
        
        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
            
            return {
                "status": "sent",
                "client_id": client_id,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger_gw.error(f"Error sending personal message to {client_id}: {e}")
            await self.disconnect(client_id)
            return {"error": str(e)}

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "subscription_stats": {
                event_type.value: len(subscribers)
                for event_type, subscribers in self.event_subscribers.items()
            },
            "connection_metadata": self.connection_metadata
        }


class GraphQLSchemaBuilder:
    """
    GraphQL schema builder for defining API schema.
    Provides type-safe GraphQL schema construction.
    """

    def __init__(self):
        self.types = {}
        self.queries = {}
        self.mutations = {}
        self.subscriptions = {}

    def add_type(self, type_name: str, fields: Dict[str, str]) -> Dict[str, Any]:
        """
        Add a GraphQL type to the schema.
        
        Args:
            type_name: Name of the type
            fields: Field definitions (name -> GraphQL type)
        """
        self.types[type_name] = fields
        return {"status": "type_added", "type_name": type_name}

    def add_query(self, query_name: str, return_type: str, 
                  resolver: str, args: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Add a GraphQL query to the schema.
        
        Args:
            query_name: Name of the query
            return_type: GraphQL return type
            resolver: Resolver function name
            args: Optional query arguments
        """
        self.queries[query_name] = {
            "return_type": return_type,
            "resolver": resolver,
            "args": args or {}
        }
        return {"status": "query_added", "query_name": query_name}

    def add_mutation(self, mutation_name: str, return_type: str,
                    resolver: str, args: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Add a GraphQL mutation to the schema.
        
        Args:
            mutation_name: Name of the mutation
            return_type: GraphQL return type
            resolver: Resolver function name
            args: Optional mutation arguments
        """
        self.mutations[mutation_name] = {
            "return_type": return_type,
            "resolver": resolver,
            "args": args or {}
        }
        return {"status": "mutation_added", "mutation_name": mutation_name}

    def add_subscription(self, subscription_name: str, return_type: str,
                       resolver: str, args: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Add a GraphQL subscription to the schema.
        
        Args:
            subscription_name: Name of the subscription
            return_type: GraphQL return type
            resolver: Resolver function name
            args: Optional subscription arguments
        """
        self.subscriptions[subscription_name] = {
            "return_type": return_type,
            "resolver": resolver,
            "args": args or {}
        }
        return {"status": "subscription_added", "subscription_name": subscription_name}

    def generate_schema(self) -> str:
        """Generate the complete GraphQL schema string."""
        schema_parts = []
        
        # Add types
        for type_name, fields in self.types.items():
            field_str = ", ".join([f"{name}: {type_}" for name, type_ in fields.items()])
            schema_parts.append(f"type {type_name} {{ {field_str} }}")
        
        # Add queries
        if self.queries:
            query_parts = []
            for query_name, query_def in self.queries.items():
                args_str = ""
                if query_def["args"]:
                    args_str = f"({', '.join([f'{name}: {type_}' for name, type_ in query_def['args'].items()])})"
                query_parts.append(f"  {query_name}{args_str}: {query_def['return_type']}")
            
            schema_parts.append(f"type Query {{\n{chr(10).join(query_parts)}\n}}")
        
        # Add mutations
        if self.mutations:
            mutation_parts = []
            for mutation_name, mutation_def in self.mutations.items():
                args_str = ""
                if mutation_def["args"]:
                    args_str = f"({', '.join([f'{name}: {type_}' for name, type_ in mutation_def['args'].items()])})"
                mutation_parts.append(f"  {mutation_name}{args_str}: {mutation_def['return_type']}")
            
            schema_parts.append(f"type Mutation {{\n{chr(10).join(mutation_parts)}\n}}")
        
        # Add subscriptions
        if self.subscriptions:
            subscription_parts = []
            for subscription_name, subscription_def in self.subscriptions.items():
                args_str = ""
                if subscription_def["args"]:
                    args_str = f"({', '.join([f'{name}: {type_}' for name, type_ in subscription_def['args'].items()])})"
                subscription_parts.append(f"  {subscription_name}{args_str}: {subscription_def['return_type']}")
            
            schema_parts.append(f"type Subscription {{\n{chr(10).join(subscription_parts)}\n}}")
        
        return "\n\n".join(schema_parts)


class APIGateway:
    """
    Main API Gateway class that integrates WebSocket support,
    GraphQL schema management, and API composition.
    """

    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.graphql_builder = GraphQLSchemaBuilder()
        self.rate_limits = defaultdict(int)
        self.api_usage_stats = defaultdict(int)
        self.config = {
            "rate_limit_per_minute": 100,
            "enable_graphql": True,
            "enable_websocket": True,
            "enable_rate_limiting": True
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the API Gateway.
        
        Args:
            config: Optional configuration
        """
        if config:
            self.config.update(config)
        
        # Build default GraphQL schema
        self._build_default_schema()
        
        return {
            "status": "success",
            "config": self.config,
            "graphql_enabled": self.config["enable_graphql"],
            "websocket_enabled": self.config["enable_websocket"],
            "rate_limiting_enabled": self.config["enable_rate_limiting"],
            "initialized_at": datetime.now(timezone.utc).isoformat()
        }

    def _build_default_schema(self):
        """Build the default GraphQL schema for IBP operations."""
        # Define common types
        self.graphql_builder.add_type("Supplier", {
            "id": "ID",
            "name": "String",
            "country": "String",
            "tier": "Int",
            "riskScore": "Float",
            "esgScore": "Float"
        })

        self.graphql_builder.add_type("DemandForecast", {
            "sku": "String",
            "period": "String",
            "forecast": "Float",
            "confidence": "Float"
        })

        self.graphql_builder.add_type("InventoryPosition", {
            "sku": "String",
            "location": "String",
            "quantity": "Float",
            "reorderPoint": "Float",
            "status": "String"
        })

        self.graphql_builder.add_type("RiskAlert", {
            "id": "ID",
            "severity": "String",
            "type": "String",
            "description": "String",
            "timestamp": "String"
        })

        # Define queries
        self.graphql_builder.add_query(
            "suppliers",
            "[Supplier]",
            "get_suppliers",
            {"riskLevel": "String", "country": "String"}
        )

        self.graphql_builder.add_query(
            "demandForecast",
            "[DemandForecast]",
            "get_demand_forecast",
            {"sku": "String", "horizon": "Int"}
        )

        self.graphql_builder.add_query(
            "inventoryPosition",
            "[InventoryPosition]",
            "get_inventory_position",
            {"sku": "String", "location": "String"}
        )

        self.graphql_builder.add_query(
            "riskAlerts",
            "[RiskAlert]",
            "get_risk_alerts",
            {"severity": "String", "limit": "Int"}
        )

        # Define mutations
        self.graphql_builder.add_mutation(
            "updateDemandForecast",
            "DemandForecast",
            "update_demand_forecast",
            {"sku": "String", "period": "String", "forecast": "Float"}
        )

        self.graphql_builder.add_mutation(
            "createScenario",
            "String",
            "create_scenario",
            {"name": "String", "type": "String", "parameters": "String"}
        )

        # Define subscriptions
        self.graphql_builder.add_subscription(
            "riskAlerts",
            "RiskAlert",
            "subscribe_risk_alerts",
            {"severity": "String"}
        )

        self.graphql_builder.add_subscription(
            "inventoryUpdates",
            "InventoryPosition",
            "subscribe_inventory_updates",
            {"sku": "String"}
        )

    def get_graphql_schema(self) -> str:
        """Get the current GraphQL schema."""
        return self.graphql_builder.generate_schema()

    def check_rate_limit(self, client_id: str) -> Dict[str, Any]:
        """
        Check if a client has exceeded rate limits.
        
        Args:
            client_id: Client identifier
        """
        if not self.config["enable_rate_limiting"]:
            return {"allowed": True}
        
        current_time = datetime.now(timezone.utc)
        minute_key = f"{client_id}_{current_time.strftime('%Y%m%d-%H%M')}"
        
        self.rate_limits[minute_key] += 1
        
        if self.rate_limits[minute_key] > self.config["rate_limit_per_minute"]:
            return {
                "allowed": False,
                "limit": self.config["rate_limit_per_minute"],
                "current": self.rate_limits[minute_key],
                "reset_in": 60 - current_time.second
            }
        
        return {"allowed": True}

    def record_api_usage(self, endpoint: str, client_id: str):
        """
        Record API usage for analytics.
        
        Args:
            endpoint: API endpoint
            client_id: Client identifier
        """
        key = f"{endpoint}_{client_id}"
        self.api_usage_stats[key] += 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "total_requests": sum(self.api_usage_stats.values()),
            "endpoints": dict(self.api_usage_stats),
            "rate_limits": dict(self.rate_limits)
        }

    async def broadcast_event(self, event_type: APIEventType, data: Dict[str, Any],
                             source: str = "system") -> Dict[str, Any]:
        """
        Broadcast an event through the WebSocket manager.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Event source
        """
        event = APIEvent(event_type=event_type, data=data, source=source)
        return await self.connection_manager.broadcast(event)

    def get_gateway_stats(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics."""
        return {
            "connection_stats": self.connection_manager.get_connection_stats(),
            "usage_stats": self.get_usage_stats(),
            "config": self.config,
            "graphql_types": len(self.graphql_builder.types),
            "graphql_queries": len(self.graphql_builder.queries),
            "graphql_mutations": len(self.graphql_builder.mutations),
            "graphql_subscriptions": len(self.graphql_builder.subscriptions)
        }


# Global gateway instance
api_gateway = APIGateway()