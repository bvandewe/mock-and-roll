# Contributing to Mock-and-Roll

Thank you for your interest in contributing to Mock-and-Roll! This guide will help you get started with contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of FastAPI and REST APIs
- Familiarity with JSON configuration

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mock-and-roll.git
   cd mock-and-roll
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest black flake8 mypy pre-commit
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Start basic server
   ./mockctl start basic
   
   # Test API
   curl http://localhost:8000/api/health
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow our coding standards and architecture guidelines:

- **Code Style**: Follow PEP 8 and use Black formatter
- **Type Hints**: Always include type hints
- **Documentation**: Add docstrings to all functions and classes
- **Tests**: Write tests for new functionality

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific_feature.py

# Run with coverage
pytest --cov=src tests/
```

### 4. Format and Lint

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Use conventional commit messages:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a Pull Request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots for UI changes
- Test coverage information

## Code Standards

### Python Code Style

```python
"""
Module description explaining the purpose and main functionality.

This module handles [specific functionality] and provides [key features].
Used by [related components] for [specific use cases].
"""

import logging
from typing import Optional, Dict, Any

from fastapi import HTTPException


logger = logging.getLogger(__name__)


def example_function(data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
    """Process data with optional configuration.
    
    Args:
        data: Input data to process
        options: Optional processing configuration
        
    Returns:
        Processed result string
        
    Raises:
        HTTPException: If data is invalid
        
    Example:
        result = example_function({"key": "value"}, {"format": "json"})
    """
    try:
        # Validate input
        if not data:
            raise HTTPException(status_code=400, detail="Data is required")
        
        # Process data
        result = process_data(data, options or {})
        logger.info(f"Successfully processed {len(data)} items")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Processing failed")
```

### Configuration Standards

All new features should be configurable:

```json
{
  "feature_name": {
    "enabled": true,
    "settings": {
      "option1": "value1",
      "option2": 42
    }
  }
}
```

### Testing Standards

Write comprehensive tests:

```python
def test_feature_success():
    """Test feature with valid input."""
    # Arrange
    input_data = {"key": "value"}
    expected_result = "processed_value"
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result == expected_result


def test_feature_error_handling():
    """Test feature handles errors gracefully."""
    with pytest.raises(HTTPException) as exc_info:
        feature_function(None)
    
    assert exc_info.value.status_code == 400
```

## Architecture Guidelines

### Adding New Features

1. **Configuration First** - Make features configurable
2. **Domain-Driven** - Follow clean architecture principles
3. **Test Coverage** - Ensure adequate test coverage
4. **Documentation** - Update relevant documentation

### CLI Extensions

When extending the CLI:

```python
# Follow the established pattern
from ..domain.entities import YourEntity
from ..domain.repositories import YourRepository


class YourService:
    """Service for handling your feature."""
    
    def __init__(self, repository: YourRepository):
        self.repository = repository
    
    def your_method(self, param: str) -> YourEntity:
        """Implement your business logic."""
        pass
```

### API Extensions

For new API endpoints:

```python
# Add to handlers/routes.py
@router.get("/api/your-endpoint")
async def your_endpoint(param: str = Query(...)) -> YourResponse:
    """Handle your endpoint request."""
    try:
        result = process_request(param)
        return YourResponse(data=result)
    except Exception as e:
        logger.error(f"Error in your_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

## Documentation

### Code Documentation

- All modules must have module-level docstrings
- All functions and classes must have comprehensive docstrings
- Use Google-style docstrings with examples
- Include type hints for all parameters and return values

### User Documentation

When adding features, update:

1. **README.md** - If it affects installation or basic usage
2. **Configuration Guide** - For new configuration options
3. **CLI Reference** - For new commands or options
4. **Examples** - Provide usage examples
5. **API Reference** - For new endpoints

## Testing

### Test Categories

1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test component interactions
3. **API Tests** - Test HTTP endpoints
4. **CLI Tests** - Test command-line interface

### Running Tests

```bash
# All tests
pytest

# Specific category
pytest tests/unit/
pytest tests/integration/
pytest tests/api/

# With coverage
pytest --cov=src --cov-report=html tests/

# Parallel execution
pytest -n auto tests/
```

### Writing Tests

Follow these patterns:

```python
# Unit test
def test_function_name():
    """Test description."""
    # Arrange - Set up test data
    # Act - Execute the function
    # Assert - Check results

# Integration test  
def test_api_endpoint(client):
    """Test API endpoint integration."""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# CLI test
def test_cli_command(runner):
    """Test CLI command."""
    result = runner.invoke(cli, ["command", "--option", "value"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

## Release Process

### Version Management

We follow semantic versioning:
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes

### Release Steps

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Update documentation
5. Deploy to package repositories

## Community

### Getting Help

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community discussion
- **Documentation** - Comprehensive guides and references

### Communication

- Be respectful and constructive
- Provide clear descriptions and examples
- Search existing issues before creating new ones
- Include relevant details (versions, error messages, etc.)

## Issue Guidelines

### Bug Reports

Include:
- Python version
- Mock-and-Roll version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:
- Problem description
- Proposed solution
- Use cases
- Alternative solutions considered

### Security Issues

For security vulnerabilities:
- Do NOT create public issues
- Email security concerns to [security@example.com]
- Provide detailed information privately

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Documentation credits

Thank you for contributing to Mock-and-Roll! Your contributions help make this project better for everyone.
