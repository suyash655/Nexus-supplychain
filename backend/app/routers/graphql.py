"""
NEXUS — GraphQL Router
=======================
GraphQL endpoints for flexible data queries and mutations.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.api_gateway import api_gateway

logger_gql = logging.getLogger("nexus.graphql")

router = APIRouter(prefix="/graphql", tags=["graphql"])


class GraphQLQuery(BaseModel):
    """GraphQL query model."""
    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = None


class GraphQLResponse(BaseModel):
    """GraphQL response model."""
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None


@router.get("/schema")
async def get_graphql_schema():
    """
    Get the current GraphQL schema.

    Returns the complete GraphQL schema with all types, queries, mutations, and subscriptions.
    """
    try:
        schema = api_gateway.get_graphql_schema()
        return {
            "status": "success",
            "schema": schema,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger_gql.error(f"Error getting GraphQL schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def execute_graphql_query(request: Request, graphql_query: GraphQLQuery):
    """
    Execute a GraphQL query.

    This is a simplified GraphQL execution engine. For production use,
    consider using a full GraphQL library like graphene or strawberry.
    """
    try:
        # Check rate limit
        client_id = request.client.host if request.client else "unknown"
        rate_limit_result = api_gateway.check_rate_limit(client_id)

        if not rate_limit_result.get("allowed"):
            raise HTTPException(status_code=429, detail=rate_limit_result)

        # Record API usage
        api_gateway.record_api_usage("graphql_query", client_id)

        # Parse the query to determine operation type
        query_string = graphql_query.query.strip()

        # Simple query parsing (in production, use a proper GraphQL parser)
        if query_string.startswith("query") or query_string.startswith("{"):
            # This is a query operation
            result = await _execute_query(graphql_query.query, graphql_query.variables)
        elif query_string.startswith("mutation"):
            # This is a mutation operation
            result = await _execute_mutation(graphql_query.query, graphql_query.variables)
        elif query_string.startswith("subscription"):
            # Subscriptions are handled via WebSocket
            raise HTTPException(
                status_code=400,
                detail="Subscriptions are handled via WebSocket. Use /ws/connect endpoint."
            )
        else:
            # Assume it's a query (default)
            result = await _execute_query(graphql_query.query, graphql_query.variables)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger_gql.error(f"Error executing GraphQL query: {e}")
        return GraphQLResponse(
            errors=[{
                "message": str(e),
                "locations": [{"line": 1, "column": 1}]
            }]
        )


async def _execute_query(query: str, variables: Optional[Dict[str, Any]]) -> GraphQLResponse:
    """
    Execute a GraphQL query operation.

    This is a simplified implementation. In production, use a proper
    GraphQL execution engine like graphene or strawberry.
    """
    try:
        # Extract query name (simplified parsing)
        query_name = _extract_query_name(query)

        # Get the resolver from the schema builder
        if query_name in api_gateway.graphql_builder.queries:
            query_def = api_gateway.graphql_builder.queries[query_name]
            resolver_name = query_def["resolver"]

            # Execute the resolver (this would call the actual business logic)
            result_data = await _execute_resolver(resolver_name, variables or {})

            return GraphQLResponse(data={query_name: result_data})
        else:
            return GraphQLResponse(
                errors=[{
                    "message": f"Unknown query: {query_name}",
                    "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"}
                }]
            )

    except Exception as e:
        logger_gql.error(f"Error executing query: {e}")
        return GraphQLResponse(
            errors=[{
                "message": str(e),
                "extensions": {"code": "INTERNAL_SERVER_ERROR"}
            }]
        )


async def _execute_mutation(mutation: str, variables: Optional[Dict[str, Any]]) -> GraphQLResponse:
    """
    Execute a GraphQL mutation operation.

    This is a simplified implementation. In production, use a proper
    GraphQL execution engine like graphene or strawberry.
    """
    try:
        # Extract mutation name (simplified parsing)
        mutation_name = _extract_mutation_name(mutation)

        # Get the resolver from the schema builder
        if mutation_name in api_gateway.graphql_builder.mutations:
            mutation_def = api_gateway.graphql_builder.mutations[mutation_name]
            resolver_name = mutation_def["resolver"]

            # Execute the resolver (this would call the actual business logic)
            result_data = await _execute_resolver(resolver_name, variables or {})

            return GraphQLResponse(data={mutation_name: result_data})
        else:
            return GraphQLResponse(
                errors=[{
                    "message": f"Unknown mutation: {mutation_name}",
                    "extensions": {"code": "GRAPHQL_VALIDATION_FAILED"}
                }]
            )

    except Exception as e:
        logger_gql.error(f"Error executing mutation: {e}")
        return GraphQLResponse(
            errors=[{
                "message": str(e),
                "extensions": {"code": "INTERNAL_SERVER_ERROR"}
            }]
        )


def _extract_query_name(query: str) -> str:
    """Extract the query name from a GraphQL query string."""
    # Simplified parsing - in production use a proper GraphQL parser
    query = query.strip()
    if query.startswith("query"):
        # Extract name after "query"
        parts = query.split()
        if len(parts) > 1:
            return parts[1].replace("{", "").replace("(", "")
    else:
        # Assume first field name is the query
        if query.startswith("{"):
            content = query[1:].strip()
            first_field = content.split()[0].replace("{", "")
            return first_field
    return "unknown"


def _extract_mutation_name(mutation: str) -> str:
    """Extract the mutation name from a GraphQL mutation string."""
    # Simplified parsing - in production use a proper GraphQL parser
    mutation = mutation.strip()
    if mutation.startswith("mutation"):
        # Extract name after "mutation"
        parts = mutation.split()
        if len(parts) > 1:
            return parts[1].replace("{", "").replace("(", "")
    return "unknown"


async def _execute_resolver(resolver_name: str, variables: Dict[str, Any]) -> Any:
    """
    Execute a resolver function.

    This is a placeholder implementation. In production, this would
    call the actual business logic resolvers.
    """
    # Mock resolvers for demonstration
    resolvers = {
        "get_suppliers": lambda: [
            {"id": "1", "name": "Supplier A", "country": "USA", "tier": 1, "riskScore": 25.5, "esgScore": 85.0},
            {"id": "2", "name": "Supplier B", "country": "Germany", "tier": 2, "riskScore": 45.2, "esgScore": 72.0},
        ],
        "get_demand_forecast": lambda: [
            {"sku": "SKU001", "period": "2024-01", "forecast": 1000, "confidence": 0.85},
            {"sku": "SKU001", "period": "2024-02", "forecast": 1100, "confidence": 0.82},
        ],
        "get_inventory_position": lambda: [
            {"sku": "SKU001", "location": "Warehouse A", "quantity": 500, "reorderPoint": 200, "status": "OK"},
            {"sku": "SKU002", "location": "Warehouse B", "quantity": 150, "reorderPoint": 200, "status": "LOW"},
        ],
        "get_risk_alerts": lambda: [
            {"id": "1", "severity": "HIGH", "type": "SUPPLIER_DELAY", "description": "Supplier A delayed by 5 days", "timestamp": datetime.now(timezone.utc).isoformat()},
        ],
        "update_demand_forecast": lambda: {"sku": "SKU001", "period": "2024-01", "forecast": 1050, "confidence": 0.87},
        "create_scenario": lambda: {"id": "SCENARIO-001", "name": "Scenario 1", "status": "created"},
    }

    if resolver_name in resolvers:
        return resolvers[resolver_name]()
    else:
        logger_gql.warning(f"Unknown resolver: {resolver_name}")
        return None


@router.get("/stats")
async def get_graphql_stats():
    """
    Get GraphQL statistics and usage information.
    """
    try:
        gateway_stats = api_gateway.get_gateway_stats()

        return {
            "status": "success",
            "graphql_stats": {
                "types": gateway_stats["graphql_types"],
                "queries": gateway_stats["graphql_queries"],
                "mutations": gateway_stats["graphql_mutations"],
                "subscriptions": gateway_stats["graphql_subscriptions"]
            },
            "schema_available": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger_gql.error(f"Error getting GraphQL stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/introspection")
async def graphql_introspection():
    """
    GraphQL introspection endpoint for tool support.

    Returns schema information for GraphQL clients like GraphiQL or Apollo Studio.
    """
    try:
        api_gateway.get_graphql_schema()

        # Convert to introspection format (simplified)
        introspection = {
            "__schema": {
                "types": [
                    {
                        "name": type_name,
                        "kind": "OBJECT",
                        "description": f"GraphQL type: {type_name}"
                    }
                    for type_name in api_gateway.graphql_builder.types.keys()
                ],
                "queryType": {"name": "Query"},
                "mutationType": {"name": "Mutation"} if api_gateway.graphql_builder.mutations else None,
                "subscriptionType": {"name": "Subscription"} if api_gateway.graphql_builder.subscriptions else None
            }
        }

        return {
            "status": "success",
            "data": introspection,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger_gql.error(f"Error during introspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
