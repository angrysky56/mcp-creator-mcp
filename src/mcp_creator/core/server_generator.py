"""Server generation engine with clean, predictable interfaces."""

import logging
from pathlib import Path
from typing import Any

import aiofiles
from mcp.server.fastmcp import Context

from ..workflows.workflow_engine import WorkflowEngine
from .config import Settings
from .template_manager import TemplateManager

logger = logging.getLogger(__name__)


class ServerSpec:
    """Clean server specification with validation."""

    def __init__(
        self,
        name: str,
        description: str,
        language: str = "python",
        template_type: str = "basic",
        features: list[str] | None = None,
        output_dir: str | None = None,
    ):
        self.name = self._validate_name(name)
        self.description = description
        self.language = language
        self.template_type = template_type
        self.features = features or []
        self.output_dir = output_dir

    @staticmethod
    def _validate_name(name: str) -> str:
        """Ensure server name is valid Python identifier."""
        clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        if not clean_name[0].isalpha():
            clean_name = f"mcp_{clean_name}"
        return clean_name.lower()

    @property
    def template_key(self) -> str:
        """Template lookup key."""
        return f"{self.language}:{self.template_type}"


class ServerGenerator:
    """Elegant server generation with minimal complexity."""

    def __init__(
        self,
        template_manager: TemplateManager,
        workflow_engine: WorkflowEngine,
        settings: Settings,
    ):
        self.template_manager = template_manager
        self.workflow_engine = workflow_engine
        self.settings = settings

    async def create_server(
        self,
        name: str,
        description: str,
        language: str = "python",
        template_type: str = "basic",
        features: list[str] | None = None,
        output_dir: str | None = None,
        context: Context | None = None,
    ) -> str:
        """
        Create MCP server with intelligent defaults and clear feedback.

        Returns:
            Human-readable status with next steps
        """
        spec = ServerSpec(name, description, language, template_type, features, output_dir)

        try:
            # Validate template exists
            template = await self.template_manager.get_template(spec.template_key)
            if not template:
                return await self._suggest_alternatives(spec)

            # Determine output location
            server_dir = self._resolve_output_dir(spec)

            # Generate server files
            await self._generate_server_files(spec, template, server_dir, context)

            # Create configuration
            config_content = await self._generate_config(spec, server_dir)

            return self._format_success_message(spec, server_dir, config_content)

        except Exception as e:
            logger.error(f"Server generation failed for {spec.name}: {e}")
            return f"❌ Generation failed: {str(e)}"

    async def _suggest_alternatives(self, spec: ServerSpec) -> str:
        """Provide helpful suggestions when template not found."""
        available = await self.template_manager.list_templates(spec.language)

        if not available:
            return f"❌ No templates available for {spec.language}"

        suggestions = []
        lang_templates = available.get(spec.language, [])
        for template in lang_templates[:3]:  # Top 3 suggestions
            suggestions.append(f"• {template['name']}: {template['description']}")

        return f"""❌ Template '{spec.template_type}' not found for {spec.language}

Available alternatives:
{chr(10).join(suggestions)}

Use `list_templates` to see all options."""

    def _resolve_output_dir(self, spec: ServerSpec) -> Path:
        """Determine output directory with intelligent defaults."""
        if spec.output_dir:
            base_dir = Path(spec.output_dir)
        else:
            base_dir = self.settings.default_output_dir # Updated to default_output_dir

        server_dir = base_dir / spec.name
        server_dir.mkdir(parents=True, exist_ok=True)
        return server_dir

    async def _generate_server_files(
        self,
        spec: ServerSpec,
        template: Any,
        server_dir: Path,
        context: Context | None,
    ) -> None:
        """Generate server files with AI enhancement when available."""
        # Prepare template variables
        variables = {
            "server_name": spec.name,
            "description": spec.description,
            "features": spec.features,
            "class_name": spec.name.replace("_", " ").title().replace(" ", ""),
        }

        # Enhance with AI if context available
        if context:
            variables = await self._enhance_with_ai(variables, spec, context)

        # Render main server file
        server_content = await self.template_manager.render_template(
            spec.template_key.replace(":", "/"), variables
        )

        main_file = server_dir / "main.py"
        async with aiofiles.open(main_file, "w") as f:
            await f.write(server_content)

        # Generate additional files
        await self._generate_support_files(spec, server_dir, variables)

    async def _enhance_with_ai(
        self,
        variables: dict[str, Any],
        spec: ServerSpec,
        context: Context,
    ) -> dict[str, Any]:
        """Provide structured enhancement suggestions for server implementation."""
        try:
            # Note: AI sampling is not currently supported in Claude Desktop
            # Providing structured suggestions based on server specification

            enhancement_suggestions = {
                "tools": self._suggest_tools_for_spec(spec),
                "resources": self._suggest_resources_for_spec(spec),
                "error_handling": [
                    "Implement try/catch blocks around all external operations",
                    "Log errors to stderr for MCP compliance",
                    "Provide meaningful error messages to users",
                    "Handle network timeouts gracefully"
                ],
                "performance_tips": [
                    "Use async/await for I/O operations",
                    "Implement connection pooling for databases",
                    "Cache expensive computations",
                    "Set appropriate timeouts"
                ]
            }

            variables["ai_enhanced"] = True
            variables["ai_suggestions"] = enhancement_suggestions

        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")

        return variables

    def _suggest_tools_for_spec(self, spec: ServerSpec) -> list[dict]:
        """Suggest appropriate tools based on server specification."""
        suggested_tools = []

        # Basic tools for all servers
        suggested_tools.append({
            "name": "process_data",
            "description": f"Process data for {spec.description}",
            "parameters": ["data: str", "operation: str = 'analyze'"]
        })

        # Feature-specific suggestions
        if "database" in spec.description.lower():
            suggested_tools.append({
                "name": "query_database",
                "description": "Execute database queries safely",
                "parameters": ["query: str", "limit: int = 100"]
            })

        if "file" in spec.description.lower():
            suggested_tools.append({
                "name": "process_file",
                "description": "Process and analyze files",
                "parameters": ["file_path: str", "operation: str"]
            })

        return suggested_tools

    def _suggest_resources_for_spec(self, spec: ServerSpec) -> list[dict]:
        """Suggest appropriate resources based on server specification."""
        suggested_resources = []

        # Status resource for all servers
        suggested_resources.append({
            "name": f"{spec.name}://status",
            "description": "Server status and health information"
        })

        # Feature-specific suggestions
        if "config" in spec.description.lower():
            suggested_resources.append({
                "name": f"{spec.name}://config",
                "description": "Configuration data and settings"
            })

        return suggested_resources

    async def _generate_support_files(
        self,
        spec: ServerSpec,
        server_dir: Path,
        variables: dict[str, Any],
    ) -> None:
        """Generate supporting files (README, requirements, etc.)."""
        # Generate README
        readme_content = f"""# {spec.name.replace('_', ' ').title()}

{spec.description}

## Features
{chr(10).join(f'- {feature}' for feature in spec.features)}

## Installation
```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv add "mcp[cli]"
```

## Usage
```bash
python main.py
```

## Configuration
Add to your Claude Desktop config:
See `claude_config.json` in this directory.

Generated by MCP-Creator-MCP
"""

        readme_file = server_dir / "README.md"
        async with aiofiles.open(readme_file, "w") as f:
            await f.write(readme_content)

    async def _generate_config(self, spec: ServerSpec, server_dir: Path) -> str:
        """Generate Claude Desktop configuration."""
        config = {
            "mcpServers": {
                spec.name: {
                    "command": "uv",
                    "args": [
                        "--directory",
                        str(server_dir.absolute()),
                        "run",
                        "python",
                        "main.py"
                    ]
                }
            }
        }

        config_file = server_dir / "claude_config.json"
        import json
        config_content = json.dumps(config, indent=2)

        async with aiofiles.open(config_file, "w") as f:
            await f.write(config_content)

        return config_content

    def _format_success_message(
        self,
        spec: ServerSpec,
        server_dir: Path,
        config_content: str,
    ) -> str:
        """Format success message with clear next steps."""
        return f"""✅ MCP Server '{spec.name}' created successfully!

📁 Location: {server_dir}
🛠 Language: {spec.language}
📋 Template: {spec.template_type}
⚡ Features: {', '.join(spec.features) if spec.features else 'basic'}

📋 Next Steps:
1. Review the generated code in {server_dir}
2. Test the server: `cd {server_dir} && python main.py`
3. Add to Claude Desktop config:

{config_content}

🎉 Your MCP server is ready to use!"""

    async def cleanup(self) -> None:
        """Clean shutdown."""
        logger.info("Server generator cleaned up")
