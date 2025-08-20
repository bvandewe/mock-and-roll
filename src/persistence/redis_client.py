"""
Redis persistence and caching utilities for the mock API server.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Optional

import redis
from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError


class RedisClient:
    """Redis client wrapper with connection handling."""

    def __init__(self):
        self._client = None

    def get_client(self):
        """Get Redis client with connection handling."""
        if self._client is None:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                redis_db = int(os.getenv("REDIS_DB", "0"))
                self._client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
                # Test connection
                self._client.ping()
                logging.info(f"Connected to Redis at {redis_host}:{redis_port}")
            except RedisConnectionError:
                logging.warning("Redis connection failed. Persistence features disabled.")
                self._client = None
        return self._client


# Global Redis client instance
redis_client = RedisClient()


def get_redis_client():
    """Get the global Redis client."""
    return redis_client.get_client()


def store_entity(entity_name: str, data: dict[str, Any]) -> str:
    """Store entity in Redis and return the generated key."""
    redis_conn = get_redis_client()
    if not redis_conn:
        raise HTTPException(status_code=503, detail="Redis not available")

    entity_id = str(uuid.uuid4())
    key = f"{entity_name}.{entity_id}"

    # Add metadata
    entity_data = {"id": entity_id, "entity_type": entity_name, "created_at": datetime.utcnow().isoformat(), "data": data}

    try:
        redis_conn.setex(key, 3600, json.dumps(entity_data))  # 1 hour TTL
        logging.info(f"Stored entity: {key}")
        return entity_id
    except Exception as e:
        logging.error(f"Failed to store entity: {e}")
        raise HTTPException(status_code=500, detail="Failed to store entity")


def get_entity(entity_name: str, entity_id: str) -> Optional[dict[str, Any]]:
    """Retrieve entity from Redis."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return None

    key = f"{entity_name}.{entity_id}"
    try:
        data = redis_conn.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logging.error(f"Failed to retrieve entity {key}: {e}")
        return None


def list_entities(entity_name: str) -> list[dict[str, Any]]:
    """List all entities of a given type."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return []

    pattern = f"{entity_name}.*"
    try:
        keys = redis_conn.keys(pattern)
        entities = []
        for key in keys:
            data = redis_conn.get(key)
            if data:
                entity = json.loads(data)
                entities.append(entity)
        return entities
    except Exception as e:
        logging.error(f"Failed to list entities for {entity_name}: {e}")
        return []


def flush_cache() -> bool:
    """Flush all cache data."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return False

    try:
        redis_conn.flushdb()
        logging.info("Redis cache flushed")
        return True
    except Exception as e:
        logging.error(f"Failed to flush cache: {e}")
        return False


def get_cache_info() -> dict[str, Any]:
    """Get Redis cache information."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return {"status": "disconnected", "keys": 0}

    try:
        info = redis_conn.info()
        keys = redis_conn.dbsize()
        return {"status": "connected", "keys": keys, "memory_used": info.get("used_memory_human", "N/A"), "connected_clients": info.get("connected_clients", 0), "uptime": info.get("uptime_in_seconds", 0)}
    except Exception as e:
        logging.error(f"Failed to get cache info: {e}")
        return {"status": "error", "error": str(e)}


def delete_entity(entity_name: str, entity_id: str) -> bool:
    """Delete a specific entity from Redis."""
    redis_conn = get_redis_client()
    if not redis_conn:
        return False

    key = f"{entity_name}.{entity_id}"
    try:
        deleted = redis_conn.delete(key)
        if deleted:
            logging.info(f"Deleted entity: {key}")
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to delete entity {key}: {e}")
        return False
