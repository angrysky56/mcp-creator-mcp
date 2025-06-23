# MCP Best Practices: Structural Elegance and Cognitive Simplicity

## Architectural Principles

### Cognitive Load Reduction
- **Single Responsibility**: Each component does one thing exceptionally well
- **Predictable Patterns**: Consistent interfaces reduce mental mapping overhead
- **Clear Boundaries**: Well-defined separation between concerns
- **Explicit Dependencies**: No hidden coupling or surprising side effects

### Structural Elegance
- **Composition Over Inheritance**: Build complexity through simple, composable parts
- **Immutable Defaults**: Prefer immutable data structures where possible
- **Resource Lifecycle**: Clear initialization, operation, and cleanup phases
- **Error Boundaries**: Contained failure modes with graceful degradation

## Process Management Excellence

### Signal Handling Pattern
```python
import atexit
import signal
import sys
from typing import Set
import asyncio

# Global cleanup registry for predictable shutdown
_cleanup_tasks: Set[callable] = set()

def register_cleanup(cleanup_func: callable) -> None:
    """Register cleanup function with clear ownership."""
    _cleanup_tasks.add(cleanup_func)

def cleanup_all() -> None:
    """Execute all cleanup tasks with error isolation."""
    for cleanup_func in _cleanup_tasks:
        try:
            cleanup_func()
        except Exception as e:
            logger.warning(f"Cleanup task failed: {e}")
    _cleanup_tasks.clear()

def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals with operational clarity."""
    logger.info(f"Graceful shutdown initiated (signal {signum})")
    cleanup_all()
    sys.exit(0)

# Register handlers once, at module level
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_all)
```

### Background Task Management
```python
class TaskManager:
    """Elegant task lifecycle with clear boundaries."""
    
    def __init__(self):
        self.tasks: Set[asyncio.Task] = set()
    
    def track(self, task: asyncio.Task) -> asyncio.Task:
        """Track task with automatic cleanup on completion."""
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task
    
    async def cleanup(self) -> None:
        """Cancel all pending tasks with timeout."""
        if not self.tasks:
            return
            
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for cancellation with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.tasks, return_exceptions=True),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning("Some tasks did not cancel gracefully")
        
        self.tasks.clear()

# Usage pattern
task_manager = TaskManager()
register_cleanup(lambda: asyncio.run(task_manager.cleanup()))

# Track background tasks
async def start_background_work():
    task = asyncio.create_task(background_worker())
    task_manager.track(task)
    return task
```

## Error Handling Philosophy

### Layered Error Strategy
```python
class MCPError(Exception):
    """Base exception with operational context."""
    
    def __init__(self, message: str, context: Dict[str, Any] = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)
    
    def user_message(self) -> str:
        """Human-readable error message."""
        return f"❌ {self.message}"

class ValidationError(MCPError):
    """Input validation failures with helpful guidance."""
    pass

class ProcessingError(MCPError):
    """Processing failures with recovery suggestions."""
    pass

# Error boundary pattern
async def with_error_boundary(
    operation: callable,
    operation_name: str,
    fallback_value: Any = None
) -> Any:
    """Execute operation with comprehensive error handling."""
    try:
        return await operation()
    except ValidationError as e:
        logger.warning(f"{operation_name} validation failed: {e}")
        return e.user_message()
    except ProcessingError as e:
        logger.error(f"{operation_name} processing failed: {e}")
        return e.user_message()
    except Exception as e:
        logger.error(f"{operation_name} unexpected error: {e}")
        return f"❌ {operation_name} failed: {str(e)}"
```

## Configuration Management

### Environment-Driven Configuration
```python
from pydantic import BaseSettings, validator
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Type-safe configuration with intelligent defaults."""
    
    # Core paths with automatic creation
    output_dir: Path = Path("./mcp_servers")
    template_dir: Path = Path("./templates")
    log_level: str = "INFO"
    
    # Performance tuning
    max_concurrent: int = 3
    request_timeout: int = 30
    
    # Feature flags
    enable_caching: bool = True
    enable_metrics: bool = True
    
    @validator('output_dir', 'template_dir')
    def ensure_directory_exists(cls, path: Path) -> Path:
        """Ensure directories exist with proper permissions."""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @validator('log_level')
    def validate_log_level(cls, level: str) -> str:
        """Ensure valid logging level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Use: {valid_levels}")
        return level.upper()
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False
```

## Logging Excellence

### Operational Visibility
```python
import logging
import sys
from typing import Any, Dict

def setup_logging(level: str = "INFO") -> None:
    """Configure logging for MCP compliance and operational clarity."""
    
    # MCP servers must log to stderr
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
        force=True
    )
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

def log_operation(
    operation_name: str,
    context: Dict[str, Any] = None,
    logger: logging.Logger = None
) -> callable:
    """Decorator for automatic operation logging."""
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func: callable) -> callable:
        async def wrapper(*args, **kwargs):
            ctx_info = f" ({context})" if context else ""
            logger.info(f"Starting {operation_name}{ctx_info}")
            
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed {operation_name} successfully")
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {e}")
                raise
        
        return wrapper
    return decorator
```

## Testing Strategy

### Predictable Test Patterns
```python
import pytest
from unittest.mock import AsyncMock, patch
from typing import Any, Dict

class MCPTestBase:
    """Base test class with common patterns."""
    
    @pytest.fixture
    def mock_context(self) -> AsyncMock:
        """Mock MCP context with predictable behavior."""
        ctx = AsyncMock()
        ctx.sample.return_value = "Mock AI response"
        ctx.request_context.lifespan_context = {}
        return ctx
    
    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """Standard test data for predictable scenarios."""
        return {
            "valid_input": "test data",
            "empty_input": "",
            "large_input": "x" * 10000,
            "special_chars": "!@#$%^&*()"
        }

# Test pattern for tools
@pytest.mark.asyncio
async def test_tool_happy_path(mock_context, sample_data):
    """Test successful tool execution."""
    result = await my_tool(mock_context, sample_data["valid_input"])
    
    assert "✅" in result
    assert mock_context.sample.called

@pytest.mark.asyncio  
async def test_tool_error_handling(mock_context, sample_data):
    """Test graceful error handling."""
    mock_context.sample.side_effect = Exception("Network error")
    
    result = await my_tool(mock_context, sample_data["valid_input"])
    
    assert "❌" in result
    assert "Network error" in result
```

## Performance Considerations

### Resource Management
```python
from contextlib import asynccontextmanager
from typing import AsyncIterator
import aiofiles

@asynccontextmanager
async def managed_resource(resource_path: str) -> AsyncIterator[Any]:
    """Resource management with guaranteed cleanup."""
    resource = None
    try:
        resource = await acquire_resource(resource_path)
        yield resource
    finally:
        if resource:
            await resource.cleanup()

# Usage pattern
async def process_file(file_path: str) -> str:
    async with managed_resource(file_path) as file_handle:
        return await process_data(file_handle)
```

### Caching Strategy
```python
from functools import lru_cache
from typing import Optional
import asyncio

class AsyncLRUCache:
    """Simple async LRU cache with clear eviction."""
    
    def __init__(self, max_size: int = 128):
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.max_size = max_size
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            if key in self.cache:
                # Move to end (most recent)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
    
    async def set(self, key: str, value: Any) -> None:
        async with self.lock:
            if key in self.cache:
                self.access_order.remove(key)
            elif len(self.cache) >= self.max_size:
                # Evict least recently used
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)
```

The goal is creating MCP servers that are not just functional, but elegant, maintainable, and cognitively simple. Every design decision should reduce mental overhead while enabling sophisticated functionality.
