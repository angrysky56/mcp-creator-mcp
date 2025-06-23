"""AI guidance content management with clean abstractions."""

import logging
from pathlib import Path

import aiofiles

logger = logging.getLogger(__name__)


class ContentManager:
    """Elegant content management for AI guidance topics."""

    def __init__(self):
        self.content_cache: dict[str, str] = {}
        self.guidance_dir = Path(__file__).parent.parent.parent.parent / "ai_guidance" / "prompts"

    async def get_guidance(self, topic: str) -> str:
        """
        Retrieve guidance content with intelligent caching.

        Args:
            topic: Guidance topic (sampling, resources, tools, prompts, best-practices)

        Returns:
            Guidance content for the specified topic
        """
        # Normalize topic name
        topic_key = topic.lower().replace("-", "_")

        # Check cache first
        if topic_key in self.content_cache:
            return self.content_cache[topic_key]

        # Load from file
        content = await self._load_content(topic_key)

        # Cache for future use
        self.content_cache[topic_key] = content

        return content

    async def _load_content(self, topic: str) -> str:
        """Load content from file with graceful fallback."""
        content_file = self.guidance_dir / f"{topic}.md"

        if content_file.exists():
            try:
                async with aiofiles.open(content_file) as f:
                    return await f.read()
            except Exception as e:
                logger.warning(f"Failed to load guidance for {topic}: {e}")

        # Fallback to default content
        return await self._get_default_content(topic)

    async def _get_default_content(self, topic: str) -> str:
        """Provide default guidance content when files aren't available."""
        default_guidance = {
            "sampling": self._sampling_guidance(),
            "resources": self._resources_guidance(),
            "tools": self._tools_guidance(),
            "prompts": self._prompts_guidance(),
            "best_practices": self._best_practices_guidance(),
        }

        return default_guidance.get(topic, f"Guidance for '{topic}' is not yet available.")

    def _sampling_guidance(self) -> str:
        """Default sampling guidance content."""
        return """# MCP Sampling Guide

## What is Sampling?

Sampling allows your MCP server to delegate text generation back to the client's LLM. This creates a powerful bidirectional communication pattern.

## Key Benefits

- **Scalability**: Distribute LLM workload across clients
- **Cost Efficiency**: Clients handle their own AI costs
- **Flexibility**: Works with any LLM the client chooses

## Implementation Pattern

```python
@mcp.tool()
async def analyze_data(ctx: Context, data: str) -> str:
    prompt = f"Analyze this data: {data}"
    analysis = await ctx.sample(prompt)
    return analysis
```

## Best Practices

1. Use sampling for text generation and analysis
2. Keep prompts focused and specific
3. Handle sampling failures gracefully
4. Cache results when appropriate

## Security Considerations

- Validate all sampled content
- Don't expose sensitive data in prompts
- Implement timeouts for sampling requests
"""

    def _resources_guidance(self) -> str:
        """Default resources guidance content."""
        return """# MCP Resources Guide

## What are Resources?

Resources provide data to LLMs - think of them as GET endpoints that supply context without side effects.

## Types of Resources

### Static Resources
- Configuration data
- Documentation
- Fixed content

### Dynamic Resources
- Database queries
- API responses
- Real-time data

## Implementation Pattern

```python
@mcp.resource("data://{table_name}")
async def get_table_data(table_name: str) -> str:
    # Fetch data dynamically
    data = await database.query(table_name)
    return json.dumps(data)
```

## Best Practices

1. Keep resources focused and specific
2. Implement proper error handling
3. Use caching for expensive operations
4. Validate resource parameters
5. Return structured data when possible

## Security Guidelines

- Validate all input parameters
- Implement access controls
- Sanitize sensitive data
- Use read-only operations when possible
"""

    def _tools_guidance(self) -> str:
        """Default tools guidance content."""
        return """# MCP Tools Guide

## What are Tools?

Tools are functions that LLMs can call to perform actions - think of them as POST endpoints that can have side effects.

## Tool Design Principles

- **Single Responsibility**: Each tool should do one thing well
- **Clear Interface**: Descriptive names and comprehensive docstrings
- **Error Handling**: Graceful failure with helpful messages
- **Validation**: Always validate inputs

## Implementation Pattern

```python
@mcp.tool()
async def send_email(
    ctx: Context,
    to: str,
    subject: str,
    body: str
) -> str:
    \"\"\"
    Send an email to a recipient.

    Args:
        to: Email address of recipient
        subject: Email subject line
        body: Email message body

    Returns:
        Confirmation message with send status
    \"\"\"
    try:
        # Validate email format
        if not is_valid_email(to):
            return "❌ Invalid email address"

        # Send email
        await email_service.send(to, subject, body)
        return f"✅ Email sent to {to}"

    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return f"❌ Failed to send email: {str(e)}"
```

## Best Practices

1. Use type hints for all parameters
2. Provide comprehensive docstrings
3. Implement proper error handling
4. Return human-readable messages
5. Log important events to stderr
6. Validate all inputs
7. Use appropriate status indicators (✅, ❌, ⚠️)
"""

    def _prompts_guidance(self) -> str:
        """Default prompts guidance content."""
        return """# MCP Prompts Guide

## What are Prompts?

Prompts are pre-defined templates that help users accomplish specific tasks with consistent results.

## Prompt Types

### Simple Templates
- Text transformation prompts
- Formatting templates
- Quick actions

### Complex Workflows
- Multi-step processes
- Context-aware prompts
- Dynamic content generation

## Implementation Pattern

```python
@mcp.prompt()
def code_review_prompt(code: str, language: str) -> str:
    \"\"\"
    Generate a comprehensive code review prompt.

    Args:
        code: Code to review
        language: Programming language

    Returns:
        Formatted prompt for code review
    \"\"\"
    return f\"\"\"
    Please review this {language} code for:

    1. Code quality and style
    2. Potential bugs or issues
    3. Performance considerations
    4. Security vulnerabilities
    5. Suggestions for improvement

    Code to review:
    ```{language}
    {code}
    ```

    Provide specific, actionable feedback with examples.
    \"\"\"
```

## Best Practices

1. Make prompts specific and actionable
2. Include context and examples
3. Use clear formatting and structure
4. Test prompts with various inputs
5. Provide helpful parameter descriptions
6. Consider prompt injection prevention
"""

    def _best_practices_guidance(self) -> str:
        """Default best practices guidance content."""
        return """# MCP Server Best Practices

## Process Management & Cleanup

### Signal Handling
Always implement proper signal handlers:

```python
import signal
import sys
import atexit

def cleanup():
    \"\"\"Clean up resources on shutdown\"\"\"
    # Close connections, stop background tasks
    logger.info("Server shutting down")

def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup)
```

### Background Task Management
Track and clean up background tasks:

```python
background_tasks = set()

def track_task(task):
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

# In cleanup()
for task in background_tasks:
    if not task.done():
        task.cancel()
```

## Security Considerations

1. **Input Validation**: Always validate and sanitize inputs
2. **Rate Limiting**: Implement request rate limiting
3. **Authentication**: Use proper authentication when needed
4. **Environment Variables**: Store secrets in environment variables
5. **Least Privilege**: Grant minimal necessary permissions

## Performance Optimization

1. **Async/Await**: Use async patterns properly
2. **Caching**: Cache expensive operations
3. **Connection Pooling**: Reuse database connections
4. **Timeouts**: Set appropriate timeouts
5. **Resource Limits**: Implement resource constraints

## Error Handling

1. **Comprehensive Handling**: Catch and handle all exceptions
2. **Meaningful Messages**: Provide helpful error messages
3. **Logging**: Log errors to stderr for MCP compliance
4. **Graceful Degradation**: Fail gracefully when possible

## Code Quality

1. **Type Hints**: Use type hints throughout
2. **Docstrings**: Document all public functions
3. **Single Responsibility**: Keep functions focused
4. **Consistent Patterns**: Use consistent coding patterns
5. **Testing**: Write tests for critical functionality

## Logging Standards

Configure logging for MCP compliance:

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # MCP requirement
)
```
"""
