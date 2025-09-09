# GitHub Copilot Instructions for Mock-and-Roll

## Project Overview

Mock-and-Roll is a highly configurable and extensible mock REST API server built with FastAPI. It allows quick creation of mock endpoints with various authentication methods, conditional responses, and dynamic path parameters. The project emphasizes configuration-driven development, maintainability, and comprehensive testing.

## Code Quality Standards

### 1. Python Code Style

- **Line Length**: Maximum 500 characters (configured in pyproject.toml)
- **Formatting**: Use Black formatter with line-length=500
- **Linting**: Follow flake8 rules with E501 ignored
- **Type Hints**: Always use type hints for function parameters and return values
- **Imports**: Use absolute imports from the `src` directory

```python
# Good
from config.loader import load_api_config
from typing import Optional, Any

def process_data(data: dict[str, Any]) -> Optional[str]:
    """Process input data and return formatted result."""
    pass

# Bad  
from .loader import load_api_config

def process_data(data):
    pass
```

### 2. Documentation Requirements

#### Module-Level Documentation
Every Python file must start with a comprehensive docstring:

```python
"""
Module description explaining the purpose and main functionality.

This module handles [specific functionality] and provides [key features].
Used by [related components] for [specific use cases].
"""
```

#### Function/Method Documentation
All functions and methods must have docstrings following Google style:

```python
def create_dynamic_model(schema: dict[str, Any], model_name: str = "DynamicRequest") -> type[BaseModel]:
    """Create a Pydantic model dynamically from a JSON schema.
    
    Args:
        schema: JSON schema dictionary defining the model structure
        model_name: Name for the generated model class
        
    Returns:
        Dynamically created Pydantic BaseModel class
        
    Raises:
        ValueError: If schema is invalid or malformed
        
    Example:
        schema = {"properties": {"name": {"type": "string"}}}
        Model = create_dynamic_model(schema, "UserModel")
    """
```

#### Class Documentation
Classes must have comprehensive docstrings:

```python
class RedisClient:
    """Redis client singleton for caching and data persistence.
    
    Provides centralized Redis connection management and common operations
    for storing, retrieving, and managing cached entities. Handles connection
    failures gracefully and provides fallback behavior.
    
    Attributes:
        _instance: Singleton instance of the Redis client
        _redis: Redis connection object
        
    Example:
        client = RedisClient()
        client.store_entity("users", {"id": "123", "name": "John"})
    """
```

### 3. Configuration-Driven Development

All new features must be configurable through JSON configuration files in the `configs/` directory:

- **API Configuration** (`api.json`): API metadata, server settings, system authentication
- **Authentication Configuration** (`auth.json`): Authentication methods and security settings  
- **Endpoints Configuration** (`endpoints.json`): Dynamic endpoint definitions and responses

The project supports multiple configuration profiles (basic, persistence, vmanage) stored in separate folders under `configs/`.

When adding new features:
1. Define configuration schema in the appropriate JSON file within a config profile
2. Update configuration loader in `config/loader.py` to handle new settings
3. Implement feature with configuration-driven behavior
4. Document configuration options in README.md
5. Consider creating a new config profile if the feature significantly changes behavior

### 4. Error Handling and Logging

#### Comprehensive Error Handling
```python
import logging
from typing import Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def risky_operation(data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Perform operation that might fail gracefully.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed data or None if operation fails
        
    Raises:
        HTTPException: For client errors (400-499)
    """
    try:
        # Validate input
        if not data or not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Invalid input data provided")
            
        # Perform operation
        result = process_data(data)
        logger.info(f"Operation completed successfully for {len(data)} items")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.error(f"Validation error in risky_operation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in risky_operation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Structured Logging
Use structured logging with consistent format:

```python
logger.info(f"Processing endpoint {endpoint_path} with method {method}")
logger.warning(f"Authentication failed for user {user_id}: {reason}")
logger.error(f"Database connection failed: {error_message}", exc_info=True)
```

### 5. Testing Standards

#### Test Coverage Requirements
- **Unit Tests**: All new functions and methods must have unit tests
- **Integration Tests**: API endpoints must have integration tests
- **Configuration Tests**: New configuration options must be tested

#### Test Structure
```python
#!/usr/bin/env python3
"""
Test module for [component name] functionality.

Tests cover [list of test areas] to ensure [expected behavior].
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from module_name import function_to_test


def test_successful_operation():
    """Test function_name with valid input returns expected result."""
    # Arrange
    input_data = {"key": "value"}
    expected_result = {"processed": True}
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_result
    

def test_invalid_input_handling():
    """Test function_name handles invalid input gracefully."""
    # Arrange
    invalid_input = None
    
    # Act & Assert
    try:
        result = function_to_test(invalid_input)
        # If no exception is raised, check for appropriate error response
        assert result is None or "error" in result
    except ValueError as e:
        # Acceptable to raise ValueError for invalid input
        assert "Invalid input" in str(e)
```

#### Test File Naming
- Unit tests: `test_[module_name].py`
- Integration tests: `test_[feature]_integration.py`
- Configuration tests: `test_[config_type]_validation.py`

### 6. FastAPI Best Practices

#### Endpoint Definition
```python
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

class ResponseModel(BaseModel):
    """Response model for endpoint."""
    success: bool
    data: Optional[dict[str, Any]] = None
    message: str

@app.get("/api/v1/endpoint", 
         response_model=ResponseModel,
         summary="Brief endpoint description",
         description="Detailed endpoint functionality explanation",
         tags=["category"])
async def endpoint_handler(
    param: str = Query(..., description="Required parameter description"),
    optional_param: Optional[int] = Query(None, description="Optional parameter")
) -> ResponseModel:
    """Handle endpoint request with proper validation and error handling.
    
    Args:
        param: Required string parameter
        optional_param: Optional integer parameter
        
    Returns:
        Response model with operation result
        
    Raises:
        HTTPException: For validation errors or operation failures
    """
    try:
        # Implementation
        result = process_request(param, optional_param)
        return ResponseModel(success=True, data=result, message="Operation successful")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in endpoint_handler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Dependency Injection
Use FastAPI's dependency injection for authentication and shared resources:

```python
from fastapi import Depends

def get_redis_client() -> RedisClient:
    """Dependency to get Redis client instance."""
    return RedisClient()

async def verify_authentication(api_key: str = Header(...)) -> str:
    """Verify API key authentication."""
    if not is_valid_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.get("/protected-endpoint")
async def protected_endpoint(
    auth: str = Depends(verify_authentication),
    redis: RedisClient = Depends(get_redis_client)
):
    """Protected endpoint with authentication and Redis dependency."""
    pass
```

### 7. File and Module Organization

#### Directory Structure Adherence
Maintain the established directory structure:

```
src/
├── app/           # FastAPI application factory
├── auth/          # Authentication and security
├── cli/           # Command-line interface
├── config/        # Configuration loading and management
├── handlers/      # Request handlers and routing
├── middleware/    # Custom middleware components
├── models/        # Pydantic models and schemas
├── persistence/   # Data persistence (Redis, etc.)
├── processing/    # Business logic and data processing
└── routes/        # Route definitions and management
```

#### Import Organization
```python
# Standard library imports
import json
import logging
from typing import Optional, Dict, Any

# Third-party imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

# Local imports
from config.loader import load_api_config
from models.dynamic import create_dynamic_model
from persistence.redis_client import RedisClient
```

### 8. Configuration Management

#### Configuration Structure
The project uses a three-tier configuration structure in the `configs/` directory:

```
configs/
├── basic/          # Simple mock API configuration
│   ├── api.json
│   ├── auth.json
│   └── endpoints.json
├── persistence/    # Configuration with Redis persistence
│   ├── api.json
│   ├── auth.json
│   └── endpoints.json
└── vmanage/        # Cisco vManage API simulation
    ├── api.json
    ├── auth.json
    ├── endpoints.json
    └── README.md
```

#### Environment Variables
The configuration loader supports these environment variables:
- `MOCK_CONFIG_FOLDER`: Override default config directory path
- `CONFIG_FOLDER`: Alternative environment variable for config path
- `REDIS_HOST`: Redis server hostname (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)

#### Adding New Configuration Options
1. **Define Schema**: Add new options to appropriate JSON config file
2. **Update Loader**: Modify `config/loader.py` to handle new options
3. **Validate Configuration**: Add validation logic for new settings
4. **Document Options**: Update README.md with configuration documentation

Example:
```python
def load_feature_config() -> dict[str, Any]:
    """Load feature-specific configuration with validation.
    
    Returns:
        Validated feature configuration dictionary
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    config = load_json_config("feature.json")
    
    # Validate required fields
    required_fields = ["enabled", "settings"]
    for field in required_fields:
        if field not in config:
            raise ConfigurationError(f"Missing required field: {field}")
    
    return config
```

### 9. CLI Tool Development

The `mockctl` CLI tool follows these patterns for command management:

#### Command Structure
```python
def create_parser(self) -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(description="Mock API Server CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a mock server")
    start_parser.add_argument("--config", "-c", help="Configuration profile to use")
    start_parser.add_argument("--port", "-p", type=int, help="Port to run on")
    start_parser.set_defaults(func=self.handle_start)
    
    return parser
```

#### Server State Management
The CLI maintains server state in JSON files and provides process management:
- Process tracking by PID and port
- Configuration profile association
- Automatic cleanup of dead processes
- Interactive configuration selection

When extending the `mockctl` CLI tool:

```python
def add_new_command(self) -> None:
    """Add new command to CLI parser.
    
    Follow the established pattern for command definition:
    1. Add subparser with help text
    2. Define all arguments with descriptions
    3. Set command handler function
    4. Add input validation
    """
    parser = self.subparsers.add_parser(
        "command-name",
        help="Brief command description",
        description="Detailed command functionality"
    )
    parser.add_argument(
        "--option",
        type=str,
        help="Option description with usage example"
    )
    parser.set_defaults(func=self.handle_command)
```

### 10. Documentation Maintenance

#### README.md Updates
When adding new features, always update the README.md:

1. **Table of Contents**: Add new sections to TOC
2. **Feature Documentation**: Document new functionality with examples
3. **Configuration**: Document new configuration options
4. **API Examples**: Provide usage examples for new endpoints
5. **Installation**: Update if new dependencies are added

#### Code Comments
Use meaningful comments for complex logic:

```python
def complex_algorithm(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Process data using complex business logic."""
    
    # Group items by category for efficient processing
    categorized_data = defaultdict(list)
    for item in data:
        category = item.get("category", "default")
        categorized_data[category].append(item)
    
    # Apply transformation rules based on category-specific logic
    # This handles the business requirement for differential processing
    results = {}
    for category, items in categorized_data.items():
        if category == "priority":
            # Priority items need immediate processing
            results[category] = process_priority_items(items)
        else:
            # Standard items can be batch processed
            results[category] = process_standard_items(items)
    
    return results
```

## Pre-commit Checklist

Before committing any changes:

1. **Code Quality**:
   - [ ] All functions have type hints and docstrings
   - [ ] Code follows Black formatting (line-length=500)
   - [ ] No flake8 violations
   - [ ] Error handling is comprehensive

2. **Testing**:
   - [ ] Unit tests written for new functionality
   - [ ] Integration tests for new endpoints
   - [ ] All tests pass locally
   - [ ] Test coverage maintained

3. **Documentation**:
   - [ ] README.md updated for new features
   - [ ] Configuration options documented
   - [ ] API examples provided
   - [ ] Code comments added for complex logic

4. **Configuration**:
   - [ ] New features are configurable
   - [ ] Configuration validation added
   - [ ] Default values provided
   - [ ] Backward compatibility maintained

## Example Implementation

Here's a complete example following all guidelines:

```python
"""
Feature processing module for advanced data transformation.

This module provides functionality for processing feature data with
configurable transformation rules and caching support.
"""

import logging
from typing import Any, Optional
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, Field

from config.loader import load_feature_config
from persistence.redis_client import RedisClient

logger = logging.getLogger(__name__)


class FeatureRequest(BaseModel):
    """Request model for feature processing endpoint."""
    
    data: list[dict[str, Any]] = Field(..., description="Input data to process")
    options: Optional[dict[str, Any]] = Field(None, description="Processing options")


class FeatureResponse(BaseModel):
    """Response model for feature processing endpoint."""
    
    success: bool = Field(..., description="Processing success status")
    processed_count: int = Field(..., description="Number of items processed")
    results: dict[str, Any] = Field(..., description="Processing results")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")


class FeatureProcessor:
    """Advanced feature processor with caching and configuration support.
    
    Provides configurable data transformation with Redis caching for
    improved performance on repeated operations.
    
    Attributes:
        config: Feature processing configuration
        redis_client: Redis client for caching
        
    Example:
        processor = FeatureProcessor()
        result = await processor.process_features(request_data)
    """
    
    def __init__(self):
        """Initialize processor with configuration and Redis client."""
        self.config = load_feature_config()
        self.redis_client = RedisClient()
        logger.info("FeatureProcessor initialized with configuration")
    
    async def process_features(
        self, 
        request: FeatureRequest
    ) -> FeatureResponse:
        """Process feature data with caching and transformation.
        
        Args:
            request: Feature processing request with data and options
            
        Returns:
            Feature processing response with results
            
        Raises:
            HTTPException: For validation errors or processing failures
        """
        try:
            # Validate input data
            if not request.data:
                raise ValueError("No data provided for processing")
            
            # Check cache for existing results
            cache_key = self._generate_cache_key(request)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Returning cached result for key {cache_key}")
                return cached_result
            
            # Process data with configured transformations
            processed_data = self._apply_transformations(request.data, request.options)
            
            # Create response
            response = FeatureResponse(
                success=True,
                processed_count=len(processed_data),
                results=processed_data
            )
            
            # Cache result if caching is enabled
            if self.config.get("caching", {}).get("enabled", False):
                self._cache_result(cache_key, response)
            
            logger.info(f"Successfully processed {len(request.data)} items")
            return response
            
        except ValueError as e:
            logger.error(f"Validation error in process_features: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in process_features: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Feature processing failed")
    
    def _apply_transformations(
        self, 
        data: list[dict[str, Any]], 
        options: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Apply configured transformations to input data.
        
        Args:
            data: Input data to transform
            options: Optional transformation options
            
        Returns:
            Transformed data dictionary
        """
        # Implementation details...
        pass
    
    def _generate_cache_key(self, request: FeatureRequest) -> str:
        """Generate cache key for request."""
        # Implementation details...
        pass
    
    def _get_cached_result(self, cache_key: str) -> Optional[FeatureResponse]:
        """Retrieve cached result if available."""
        # Implementation details...
        pass
    
    def _cache_result(self, cache_key: str, response: FeatureResponse) -> None:
        """Cache processing result."""
        # Implementation details...
        pass
```

## Conclusion

Following these guidelines ensures consistent, maintainable, and well-documented code that aligns with the Mock-and-Roll project's architecture and quality standards. Always prioritize configuration-driven development, comprehensive testing, and thorough documentation for sustainable project growth.
