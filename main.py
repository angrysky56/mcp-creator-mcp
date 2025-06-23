"""
MCP Creator - A meta-MCP server for creating other MCP servers with AI guidance.

This module serves as the primary entry point for the MCP Creator server,
providing a clean interface for server generation and management.
"""

import asyncio
import logging
import signal
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import Context, FastMCP

from src.mcp_creator.core.config import Settings
from src.mcp_creator.core.server_generator import ServerGenerator
from src.mcp_creator.core.template_manager import TemplateManager
from src.mcp_creator.workflows.workflow_engine import WorkflowEngine

# Configure logging to stderr for MCP compliance
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Global components for lifecycle management
_components: dict[str, object] = {}


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict[str, object]]:
    """Manage application lifecycle with proper resource cleanup."""
    logger.info("Initializing MCP Creator components")

    try:
        # Initialize core components
        settings = Settings()
        template_manager = TemplateManager(settings)
        workflow_engine = WorkflowEngine(settings)
        server_generator = ServerGenerator(template_manager, workflow_engine, settings)

        # Load templates and workflows
        await template_manager.initialize()
        await workflow_engine.initialize()

        components = {
            "settings": settings,
            "template_manager": template_manager,
            "workflow_engine": workflow_engine,
            "server_generator": server_generator,
        }

        _components.update(components)
        logger.info("MCP Creator initialization complete")

        yield components

    except Exception as e:
        logger.error(f"Failed to initialize MCP Creator: {e}")
        raise
    finally:
        logger.info("Shutting down MCP Creator")
        # Cleanup components
        for component in _components.values():
            cleanup_method = getattr(component, "cleanup", None)
            if callable(cleanup_method):
                if asyncio.iscoroutinefunction(cleanup_method):
                    await cleanup_method()
                else:
                    cleanup_method()
        _components.clear()


# Initialize MCP server with lifespan management
mcp = FastMCP("MCP-Creator", lifespan=app_lifespan)


@mcp.tool()
async def create_mcp_server(
    ctx: Context,
    name: str,
    description: str,
    language: str = "python",
    template_type: str = "basic",
    features: list[str] | None = None,
    output_dir: str | None = None,
) -> str:
    """
    Create a new MCP server based on specifications.

    Args:
        name: Name of the MCP server (must be valid Python identifier)
        description: Description of what the server does
        language: Programming language (python, gradio, typescript)
        template_type: Type of template (basic, advanced, database, etc.)
        features: list of features to include (tools, resources, prompts, sampling)
        output_dir: Output directory (defaults to configured default)

    Returns:
        Status message with creation details and next steps
    """
    try:
        generator = ctx.request_context.lifespan_context["server_generator"]

        result = await generator.create_server(
            name=name,
            description=description,
            language=language,
            template_type=template_type,
            features=features or [],
            output_dir=output_dir,
            context=ctx,
        )

        logger.info(f"Successfully created MCP server: {name}")
        return result

    except Exception as e:
        logger.error(f"Failed to create MCP server {name}: {e}")
        return f"❌ Error creating server: {str(e)}"


@mcp.tool()
async def list_templates(ctx: Context, language: str | None = None) -> str:
    """
    list available templates for MCP server creation.

    Args:
        language: Filter by language (optional)

    Returns:
        Formatted list of available templates
    """
    try:
        template_manager = ctx.request_context.lifespan_context["template_manager"]
        templates = await template_manager.list_templates(language=language)

        if not templates:
            return "No templates available"

        result = "📋 Available Templates:\n\n"
        for lang, template_list in templates.items():
            result += f"**{lang.upper()}:**\n"
            for template in template_list:
                result += f"  • {template['name']}: {template['description']}\n"
            result += "\n"

        return result

    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        return f"❌ Error listing templates: {str(e)}"


@mcp.tool()
async def get_ai_guidance(
    ctx: Context,
    topic: str,
    server_type: str = "general",
) -> str:
    """
    Get AI-powered guidance for MCP server development.

    Args:
        topic: Topic to get guidance on (best_practices, security, performance, etc.)
        server_type: Type of server for contextualized advice

    Returns:
        AI-generated guidance and recommendations
    """
    try:
        guidance_prompt = f"""
        Provide comprehensive guidance for MCP server development on the topic: {topic}
        Context: Creating a {server_type} MCP server

        Please include:
        1. Key best practices
        2. Common pitfalls to avoid
        3. Security considerations
        4. Performance optimization tips
        5. Specific recommendations for this server type

        Format the response clearly with actionable advice.
        """

        # Use context.sample for AI-powered guidance.
        # The MCP client (e.g., Claude Desktop) is responsible for having an AI provider configured.
        # The server itself does not need API keys in its own environment for ctx.sample() to work.
        guidance = await ctx.sample(guidance_prompt)
        return f"🧠 AI Guidance - {topic.title()}:\n\n{guidance}"

    except Exception as e:
        logger.error(f"Failed to get AI guidance for topic '{topic}': {e}")
        return f"❌ Error getting guidance: {str(e)}"


@mcp.tool()
async def save_workflow(
    ctx: Context,
    name: str,
    description: str,
    steps: list[dict],
) -> str:
    """
    Save a creation workflow for reuse.

    Args:
        name: Workflow name
        description: Workflow description
        steps: list of workflow steps

    Returns:
        Confirmation message
    """
    try:
        workflow_engine = ctx.request_context.lifespan_context["workflow_engine"]

        workflow_id = await workflow_engine.save_workflow(
            name=name,
            description=description,
            steps=steps,
        )

        return f"✅ Workflow '{name}' saved successfully (ID: {workflow_id})"

    except Exception as e:
        logger.error(f"Failed to save workflow: {e}")
        return f"❌ Error saving workflow: {str(e)}"


@mcp.resource("mcp-creator://guidance/{topic}")
async def guidance_resource(topic: str) -> str:
    """
    Provide guidance resources for MCP development topics.

    Args:
        topic: Guidance topic (sampling, resources, tools, prompts, best-practices)

    Returns:
        Guidance content for the specified topic
    """
    try:
        from src.mcp_creator.ai_guidance.content_manager import ContentManager

        content_manager = ContentManager()
        guidance = await content_manager.get_guidance(topic)

        return guidance

    except Exception as e:
        logger.error(f"Failed to get guidance resource: {e}")
        return f"Error retrieving guidance for {topic}: {str(e)}"


# Cleanup handlers for graceful shutdown
def cleanup() -> None:
    """Clean up resources on shutdown."""
    logger.info("MCP Creator server shutting down")


def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down")
    cleanup()
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    try:
        logger.info("Starting MCP Creator server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        cleanup()
