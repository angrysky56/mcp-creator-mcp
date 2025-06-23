"""MCP Creator - A meta-MCP server for creating other MCP servers with AI guidance."""

__version__ = "0.1.0"
__author__ = "AI Workspace"
__description__ = "A meta-MCP server for creating other MCP servers with AI guidance"

from .core.config import Settings
from .core.server_generator import ServerGenerator
from .core.template_manager import TemplateManager
from .workflows.workflow_engine import WorkflowEngine

__all__ = [
    "Settings",
    "TemplateManager",
    "ServerGenerator",
    "WorkflowEngine",
]
