"""
Cache management endpoints for Redis persistence.

Provides endpoints to view and manage Redis cache at runtime.
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException

from auth.security import create_system_auth_dependency, system_api_key
from persistence.redis_client import (
    delete_entity,
    flush_cache,
    get_cache_info,
    get_entity,
    list_entities,
)


def add_cache_management_endpoints(app: FastAPI, api_config: Optional[dict[str, Any]] = None, auth_data: Optional[dict[str, Any]] = None):
    """
    Add cache management endpoints to the FastAPI app.

    Args:
        app: FastAPI application instance
        api_config: API configuration dictionary (optional for backward compatibility)
        auth_data: Authentication configuration dictionary
    """
    router = APIRouter(prefix="/system", tags=["Cache"])

    # Create system auth dependency using the provided auth configuration
    system_config = api_config.get("system", {}) if api_config else {}
    auth_method = system_config.get("auth_method", "system_api_key")

    if auth_data:
        get_system_auth = create_system_auth_dependency(auth_data, auth_method)
    else:
        # Fallback to basic auth for backward compatibility
        def get_system_auth(api_key: str = Depends(system_api_key)):
            return api_key

    @router.get("/cache/info", summary="Get Redis cache information")
    async def get_cache_info_endpoint(auth: str = Depends(get_system_auth)):
        """Get Redis cache information and statistics."""
        try:
            return get_cache_info()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to get cache info: {str(e)}")

    @router.delete("/cache/flush", summary="Flush Redis cache")
    async def flush_cache_endpoint(auth: str = Depends(get_system_auth)):
        """Flush all data from Redis cache."""
        try:
            success = flush_cache()
            if success:
                return {"status": "success", "message": "Cache flushed successfully"}
            else:
                raise HTTPException(status_code=503, detail="Redis not available or flush failed")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to flush cache: {str(e)}")

    @router.get("/cache/entities/{entity_name}", summary="List cached entities")
    async def list_cached_entities_endpoint(entity_name: str, auth: str = Depends(get_system_auth)):
        """List all cached entities of a specific type."""
        try:
            entities = list_entities(entity_name)
            return {"status": "success", "data": {"entity_name": entity_name, "entities": entities, "count": len(entities)}}
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to list entities: {str(e)}")

    @router.get("/cache/entities/{entity_name}/{entity_id}", summary="Get cached entity")
    async def get_cached_entity_endpoint(entity_name: str, entity_id: str, auth: str = Depends(get_system_auth)):
        """Get a specific cached entity by ID."""
        try:
            entity = get_entity(entity_name, entity_id)
            if entity is None:
                raise HTTPException(status_code=404, detail=f"Entity {entity_name}:{entity_id} not found in cache")
            return {"status": "success", "data": {"entity_name": entity_name, "entity_id": entity_id, "entity": entity}}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to get entity: {str(e)}")

    @router.delete("/cache/entities/{entity_name}/{entity_id}", summary="Delete cached entity")
    async def delete_cached_entity_endpoint(entity_name: str, entity_id: str, auth: str = Depends(get_system_auth)):
        """Delete a specific cached entity by ID."""
        try:
            success = delete_entity(entity_name, entity_id)
            if success:
                return {"status": "success", "message": f"Entity {entity_name}:{entity_id} deleted from cache"}
            else:
                raise HTTPException(status_code=404, detail=f"Entity {entity_name}:{entity_id} not found in cache")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to delete entity: {str(e)}")

    # Add the router to the app
    app.include_router(router)
