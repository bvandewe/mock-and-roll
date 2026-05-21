"""
In-memory persistence for the mock API server.

Provides ephemeral storage that is lost on server restart.
Useful for testing or when no persistence is needed.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional


# In-memory store: {entity_name: {entity_id: entity_data}}
_store: dict[str, dict[str, Any]] = {}

# Track seeded/protected entity IDs: {entity_name: set(entity_ids)}
_protected_ids: dict[str, set[str]] = {}


def is_protected_entity(entity_name: str, entity_id: str) -> bool:
    """Check if an entity is a protected (seeded) resource.

    Args:
        entity_name: Logical entity collection name.
        entity_id: The entity identifier.

    Returns:
        True if the entity was part of the initial seed and is protected.
    """
    return entity_id in _protected_ids.get(entity_name, set())


def store_entity(entity_name: str, data: dict[str, Any], entity_id: Optional[str] = None) -> str:
    """Store entity in memory and return the generated ID.

    Args:
        entity_name: Logical entity collection name.
        data: Entity payload to persist.
        entity_id: Optional pre-generated identifier.

    Returns:
        The stored entity identifier.
    """
    entity_id = entity_id or str(uuid.uuid4())
    entity_data = {
        "id": entity_id,
        "entity_type": entity_name,
        "created_at": datetime.utcnow().isoformat(),
        "data": data,
    }

    if entity_name not in _store:
        _store[entity_name] = {}
    _store[entity_name][entity_id] = entity_data
    logging.info(f"Stored entity (memory): {entity_name}.{entity_id}")
    return entity_id


def get_entity(entity_name: str, entity_id: str) -> Optional[dict[str, Any]]:
    """Retrieve entity from memory."""
    return _store.get(entity_name, {}).get(entity_id)


def list_entities(entity_name: str) -> list[dict[str, Any]]:
    """List all entities of a given type."""
    return list(_store.get(entity_name, {}).values())


def delete_entity(entity_name: str, entity_id: str) -> bool:
    """Delete a specific entity from memory."""
    collection = _store.get(entity_name, {})
    if entity_id in collection:
        del collection[entity_id]
        logging.info(f"Deleted entity (memory): {entity_name}.{entity_id}")
        return True
    return False


def flush_cache() -> bool:
    """Flush all stored data."""
    _store.clear()
    logging.info("In-memory store flushed")
    return True


def get_cache_info() -> dict[str, Any]:
    """Get store information."""
    total_keys = sum(len(c) for c in _store.values())
    return {
        "status": "active",
        "backend": "memory",
        "keys": total_keys,
        "collections": list(_store.keys()),
    }


def seed_static_entities(endpoints_config: dict[str, Any]) -> None:
    """Seed in-memory store with static entities from endpoint list responses."""
    seeded_count = 0

    for endpoint in endpoints_config.get("endpoints", []):
        persistence = endpoint.get("persistence", {})
        entity_name = persistence.get("entity_name")
        action = persistence.get("action")
        list_key = persistence.get("response_list_key")

        if action != "list" or not entity_name or not list_key:
            continue

        if entity_name not in _store:
            _store[entity_name] = {}
        if entity_name not in _protected_ids:
            _protected_ids[entity_name] = set()

        for rule in endpoint.get("responses", []):
            body = rule.get("response", {}).get("body", {})
            if not isinstance(body, dict):
                continue
            static_items = body.get(list_key, [])
            if not isinstance(static_items, list):
                continue
            for item in static_items:
                if not isinstance(item, dict):
                    continue
                item_id = item.get("id")
                if not item_id:
                    continue
                if item_id not in _store[entity_name]:
                    _store[entity_name][item_id] = {
                        "id": item_id,
                        "entity_type": entity_name,
                        "created_at": datetime.utcnow().isoformat(),
                        "data": item,
                    }
                    _protected_ids[entity_name].add(item_id)
                    seeded_count += 1

    if seeded_count > 0:
        logging.info(f"Seeded {seeded_count} static entities into memory store (protected).")
