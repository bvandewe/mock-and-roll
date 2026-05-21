"""
Persistence store abstraction layer.

Selects the appropriate persistence backend based on the API configuration:
- "redis": Uses Redis for persistence (requires running Redis server).
- "file": Uses a local JSON file for persistence (no external dependencies).
- None/other: Uses in-memory storage (ephemeral, lost on restart).

All backends expose the same interface so handlers remain backend-agnostic.
"""

import logging
from typing import Any, Optional

# Module-level reference to the active backend
_backend = None


def init_store(persistence_type: Optional[str] = None) -> None:
    """Initialize the persistence store backend.

    Args:
        persistence_type: The persistence backend to use ("redis", "file", or None for in-memory).
    """
    global _backend

    if persistence_type == "redis":
        from persistence import redis_client as backend
        _backend = backend
        logging.info("Persistence backend: Redis")
    else:
        from persistence import memory_store as backend
        _backend = backend
        logging.info("Persistence backend: In-memory (ephemeral)")


def _get_backend():
    """Get the active backend, initializing to in-memory if not yet set."""
    global _backend
    if _backend is None:
        init_store(None)
    return _backend


def store_entity(entity_name: str, data: dict[str, Any], entity_id: Optional[str] = None) -> str:
    """Store entity and return the generated ID."""
    return _get_backend().store_entity(entity_name, data, entity_id=entity_id)


def get_entity(entity_name: str, entity_id: str) -> Optional[dict[str, Any]]:
    """Retrieve entity by name and ID."""
    return _get_backend().get_entity(entity_name, entity_id)


def list_entities(entity_name: str) -> list[dict[str, Any]]:
    """List all entities of a given type."""
    return _get_backend().list_entities(entity_name)


def delete_entity(entity_name: str, entity_id: str) -> bool:
    """Delete a specific entity."""
    return _get_backend().delete_entity(entity_name, entity_id)


def is_protected_entity(entity_name: str, entity_id: str) -> bool:
    """Check if an entity is protected (seeded from initial config)."""
    backend = _get_backend()
    if hasattr(backend, "is_protected_entity"):
        return backend.is_protected_entity(entity_name, entity_id)
    return False


def flush_cache() -> bool:
    """Flush all stored data."""
    return _get_backend().flush_cache()


def get_cache_info() -> dict[str, Any]:
    """Get store information and statistics."""
    return _get_backend().get_cache_info()


def seed_static_entities(endpoints_config: dict[str, Any]) -> None:
    """Seed static entities from endpoint configurations."""
    return _get_backend().seed_static_entities(endpoints_config)
