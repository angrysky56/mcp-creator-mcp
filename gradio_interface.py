"""
Gradio interface for MCP Creator with elegant, intuitive design.

Provides a clean, user-friendly interface for creating MCP servers without
requiring deep technical knowledge while maintaining full power for experts.
"""

import asyncio
import json
import logging
import traceback
from pathlib import Path
from typing import Optional

import gradio as gr
from gradio.themes.soft import Soft

from src.mcp_creator.core.config import Settings
from src.mcp_creator.core.server_generator import ServerGenerator
from src.mcp_creator.core.template_manager import TemplateManager
from src.mcp_creator.workflows.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class MCPCreatorInterface:
    """Clean, intuitive interface for MCP server creation."""

    def __init__(self):
        self.settings = Settings()
        self.template_manager = TemplateManager(self.settings)
        self.workflow_engine = WorkflowEngine(self.settings)
        self.server_generator = ServerGenerator(
            self.template_manager,
            self.workflow_engine,
            self.settings
        )
        self._initialized = False

    async def initialize(self):
        """Initialize components asynchronously."""
        if not self._initialized:
            await self.template_manager.initialize()
            await self.workflow_engine.initialize()
            self._initialized = True

    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface with clean, intuitive design."""
        with gr.Blocks(
            title="MCP Creator",
            theme=Soft(
                primary_hue="blue",
                secondary_hue="gray",
                neutral_hue="slate"
            ),
            css=self._get_custom_css()
        ) as interface:

            # Header with clear branding
            gr.Markdown("""
            # 🚀 MCP Creator
            **Transform ideas into production-ready MCP servers with AI guidance**

            Create sophisticated Model Context Protocol servers through intuitive workflows,
            intelligent templates, and automated best practices.
            """)

            with gr.Tabs() as tabs:
                # Main creation interface
                with gr.TabItem("🛠️ Create Server", elem_id="create-tab"):
                    self._create_server_tab()

                # Template exploration
                with gr.TabItem("📚 Templates", elem_id="templates-tab"):
                    self._create_templates_tab()

                # Workflow management
                with gr.TabItem("🔄 Workflows", elem_id="workflows-tab"):
                    self._create_workflows_tab()

                # Generated server management
                with gr.TabItem("📊 Monitor", elem_id="monitor-tab"):
                    self._create_monitoring_tab()

                # AI guidance and help
                with gr.TabItem("🧠 AI Guidance", elem_id="guidance-tab"):
                    self._create_guidance_tab()

        return interface

    def _create_server_tab(self):
        """Create the main server creation interface."""

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### Server Configuration")

                # Core settings with clear descriptions
                server_name = gr.Textbox(
                    label="Server Name",
                    placeholder="my_awesome_server",
                    info="Use lowercase letters, numbers, and underscores"
                )

                server_description = gr.Textbox(
                    label="Description",
                    placeholder="Describe what your MCP server will do...",
                    lines=3,
                    info="Be specific - this helps generate better code"
                )

                with gr.Row():
                    language = gr.Dropdown(
                        choices=["python", "gradio"],
                        value="python",
                        label="Language",
                        info="Programming language for your server"
                    )

                    template_type = gr.Dropdown(
                        choices=["basic", "database", "api", "ai_agent"],
                        value="basic",
                        label="Template Type",
                        info="Starting point for your server"
                    )

                # Feature selection with clear explanations
                features = gr.CheckboxGroup(
                    choices=[
                        ("tools", "Tools - Let AI call functions"),
                        ("resources", "Resources - Provide data to AI"),
                        ("prompts", "Prompts - Reusable templates"),
                        ("sampling", "Sampling - AI-enhanced responses"),
                        ("auth", "Authentication - Secure access")
                    ],
                    value=["tools", "resources"],
                    label="Features to Include",
                    info="Select capabilities for your server"
                )

            with gr.Column(scale=1):
                gr.Markdown("### AI Assistant")

                # AI guidance panel
                ai_suggestions = gr.Textbox(
                    label="AI Suggestions",
                    lines=8,
                    interactive=False,
                    placeholder="Click 'Get AI Help' for personalized guidance..."
                )

                get_ai_help_btn = gr.Button(
                    "🤖 Get AI Help",
                    variant="secondary"
                )

                # Quick templates
                gr.Markdown("#### Quick Start")

                quick_database = gr.Button("📊 Database Server", size="sm")
                quick_api = gr.Button("🌐 API Wrapper", size="sm")
                quick_ai = gr.Button("🧠 AI Agent", size="sm")

        # Generation controls
        gr.Markdown("---")

        with gr.Row():
            generate_btn = gr.Button(
                "🚀 Generate MCP Server",
                variant="primary",
                size="lg"
            )

            save_workflow_btn = gr.Button(
                "💾 Save as Workflow",
                variant="secondary"
            )

        # Output and results
        with gr.Row():
            generation_output = gr.Textbox(
                label="Generation Results",
                lines=12,
                interactive=False,
                show_copy_button=True
            )

        # Wire up the interactions
        self._setup_server_creation_handlers(
            server_name, server_description, language, template_type,
            features, ai_suggestions, generation_output, generate_btn,
            get_ai_help_btn, quick_database, quick_api, quick_ai
        )

    def _create_templates_tab(self):
        """Create template exploration interface."""

        gr.Markdown("### Available Templates")
        gr.Markdown("Explore our curated collection of MCP server templates")

        with gr.Row():
            with gr.Column(scale=1):
                template_filter = gr.Dropdown(
                    choices=["all", "python", "gradio"],
                    value="all",
                    label="Filter by Language"
                )

                refresh_templates = gr.Button("🔄 Refresh", size="sm")

            with gr.Column(scale=2):
                template_search = gr.Textbox(
                    placeholder="Search templates...",
                    label="Search"
                )

        # Template gallery
        templates_gallery = gr.HTML(
            value=self._get_templates_html(),
            label="Templates"
        )

        # Template details
        with gr.Row():
            template_details = gr.Textbox(
                label="Template Details",
                lines=10,
                interactive=False,
                value="Select a template to view details..."
            )

        # Wire up handlers
        def refresh_templates_handler():
            return self._get_templates_html()

        refresh_templates.click(
            fn=refresh_templates_handler,
            outputs=templates_gallery
        )

    def _get_templates_html(self) -> str:
        """Generate HTML for template gallery."""
        try:
            # The `initialize` method populates this dictionary
            templates = self.template_manager.templates.values()
            if not templates:
                return "<p>No templates found. Check your template paths.</p>"

            html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; padding: 20px;">'

            for template in templates:
                features_html = ', '.join(template.features)
                html += f'''
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; background: #f9f9f9;">
                    <h3 style="margin: 0 0 8px 0; color: #333;">{template.name}</h3>
                    <p style="margin: 8px 0; color: #666;">{template.description}</p>
                    <div style="margin: 8px 0;">
                        <span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                            {template.language}
                        </span>
                    </div>
                    <div style="margin: 8px 0; font-size: 12px; color: #888;">
                        Features: {features_html}
                    </div>
                </div>'''

            html += '</div>'
            return html

        except Exception as e:
            logger.error(f"Error generating templates HTML: {e}")
            return '<p>Error loading templates. Please try refreshing.</p>'

    def _create_workflows_tab(self):
        """Create workflow management interface."""

        gr.Markdown("### Workflow Management")
        gr.Markdown("Save and reuse creation patterns for consistent results")

        with gr.Row():
            with gr.Column():
                workflow_list = gr.Dropdown(
                    label="Saved Workflows",
                    choices=self._get_workflow_choices(),
                    interactive=True
                )

                workflow_description = gr.Textbox(
                    label="Description",
                    interactive=False,
                    lines=3,
                    value="Select a workflow to view description..."
                )

            with gr.Column():
                load_workflow_btn = gr.Button("📂 Load Workflow")
                edit_workflow_btn = gr.Button("✏️ Edit Workflow")
                delete_workflow_btn = gr.Button("🗑️ Delete", variant="stop")

        # Workflow editor
        gr.Markdown("#### Workflow Steps")

        workflow_editor = gr.Code(
            label="Workflow Configuration",
            language="json",
            lines=15,
            interactive=True,
            value=self._get_sample_workflow()
        )

        with gr.Row():
            save_workflow_changes = gr.Button("💾 Save Changes", variant="primary")
            validate_workflow = gr.Button("✅ Validate", variant="secondary")

        # Wire up basic handlers
        def validate_workflow_handler(workflow_json):
            try:
                json.loads(workflow_json)
                return "✅ Workflow JSON is valid"
            except json.JSONDecodeError as e:
                return f"❌ Invalid JSON: {str(e)}"

        validate_workflow.click(
            fn=validate_workflow_handler,
            inputs=workflow_editor,
            outputs=gr.Textbox(label="Validation Result", lines=2)
        )

    def _get_workflow_choices(self):
        """Get available workflow choices."""
        return ["Basic Server Workflow", "Database Server Workflow", "API Wrapper Workflow"]

    def _get_sample_workflow(self):
        """Get sample workflow JSON."""
        return json.dumps({
            "name": "Basic Server Workflow",
            "description": "Creates a basic MCP server with tools and resources",
            "steps": [
                {
                    "type": "template_selection",
                    "template": "basic_server",
                    "language": "python"
                },
                {
                    "type": "feature_configuration",
                    "features": ["tools", "resources"]
                },
                {
                    "type": "generation",
                    "output_dir": "./mcp_servers"
                }
            ]
        }, indent=2)

    def _create_monitoring_tab(self):
        """Create server monitoring interface."""

        gr.Markdown("### Generated Servers")
        gr.Markdown("Monitor and manage your created MCP servers")

        # Server list
        server_list = gr.Dataframe(
            headers=["Name", "Status", "Created", "Features", "Actions"],
            datatype=["str", "str", "str", "str", "str"],
            label="Your Servers",
            interactive=False,
            value=self._get_server_list_data()
        )

        # Server controls
        with gr.Row():
            refresh_servers = gr.Button("🔄 Refresh")
            test_server = gr.Button("🧪 Test Selected")
            open_folder = gr.Button("📁 Open Folder")

        # Server details and logs
        with gr.Row():
            with gr.Column():
                server_details = gr.Textbox(
                    label="Server Details",
                    lines=8,
                    interactive=False,
                    value="Select a server to view details..."
                )

            with gr.Column():
                server_logs = gr.Textbox(
                    label="Recent Logs",
                    lines=8,
                    interactive=False,
                    value="No logs available..."
                )

        # Wire up handlers
        def refresh_servers_handler():
            return self._get_server_list_data()

        refresh_servers.click(
            fn=refresh_servers_handler,
            outputs=server_list
        )

    def _get_server_list_data(self):
        """Get sample server list data."""
        try:
            # This would normally scan the output directory for generated servers
            # For now, return sample data
            return [
                ["example_server", "Ready", "2024-01-15", "tools, resources", "View"],
                ["database_connector", "Running", "2024-01-14", "tools, auth", "Stop"],
                ["api_wrapper", "Stopped", "2024-01-13", "tools", "Start"]
            ]
        except Exception as e:
            logger.error(f"Error getting server list: {e}")
            return [["Error loading servers", "Unknown", "Unknown", "Unknown", "Refresh"]]

    def _create_guidance_tab(self):
        """Create AI guidance and help interface."""

        gr.Markdown("### AI Guidance & Help")
        gr.Markdown("Get expert advice on MCP development topics")

        with gr.Row():
            guidance_topic = gr.Dropdown(
                choices=[
                    "best_practices",
                    "security",
                    "performance",
                    "sampling",
                    "resources",
                    "tools",
                    "prompts"
                ],
                label="Topic",
                value="best_practices"
            )

            server_context = gr.Textbox(
                label="Your Context",
                placeholder="Describe your specific situation...",
                lines=2
            )

        get_guidance_btn = gr.Button(
            "🧠 Get Personalized Guidance",
            variant="primary"
        )

        guidance_output = gr.Markdown(
            value="Select a topic and click 'Get Guidance' for personalized advice.",
            label="Guidance"
        )

        # Wire up guidance handler
        def get_guidance_handler(topic, context):
            try:
                guidance_content = self._get_guidance_for_topic(topic, context)
                return guidance_content
            except Exception as e:
                logger.error(f"Error getting guidance: {e}")
                return "❌ Error generating guidance. Please try again."

        get_guidance_btn.click(
            fn=get_guidance_handler,
            inputs=[guidance_topic, server_context],
            outputs=guidance_output
        )

        # Quick help sections
        gr.Markdown("#### Quick Reference")

        with gr.Accordion("MCP Concepts", open=False):
            gr.Markdown("""
            - **Tools**: Functions the AI can call to perform actions
            - **Resources**: Data sources the AI can read for context
            - **Prompts**: Reusable templates for specific tasks
            - **Sampling**: Let your server use the client's AI capabilities
            """)

        with gr.Accordion("Best Practices", open=False):
            gr.Markdown("""
            - Always validate inputs and handle errors gracefully
            - Use clear, descriptive names for tools and resources
            - Log important events to stderr for MCP compliance
            - Implement proper cleanup to prevent resource leaks
            """)

    def _get_guidance_for_topic(self, topic: str, context: str) -> str:
        """Generate guidance content for a specific topic."""
        guidance_map = {
            "best_practices": """
## MCP Best Practices

### Core Principles
- **Simplicity**: Keep your server focused on a specific domain
- **Reliability**: Handle errors gracefully and provide clear feedback
- **Security**: Validate all inputs and sanitize outputs
- **Performance**: Use async operations and efficient data structures

### Implementation Tips
- Use descriptive names for tools and resources
- Implement proper logging to stderr for MCP compliance
- Provide helpful error messages to users
- Document your server's capabilities clearly
            """,
            "security": """
## Security Guidelines

### Input Validation
- Never trust user input - always validate and sanitize
- Use parameter schemas to enforce type safety
- Implement rate limiting for resource-intensive operations

### Authentication
- Use secure authentication methods (API keys, OAuth)
- Store credentials securely (environment variables)
- Implement proper session management

### Data Protection
- Never log sensitive information
- Use HTTPS for external API calls
- Implement proper access controls
            """,
            "performance": """
## Performance Optimization

### Async Operations
- Use async/await for I/O operations
- Implement connection pooling for databases
- Cache frequently accessed data

### Resource Management
- Clean up resources properly
- Use context managers for file operations
- Implement proper error handling and cleanup

### Monitoring
- Log performance metrics
- Monitor memory usage
- Implement health checks
            """
        }

        base_guidance = guidance_map.get(topic, "No specific guidance available for this topic.")

        if context.strip():
            base_guidance += f"\n\n### Your Context\n{context}\n\n**Recommendation**: Based on your context, focus on implementing proper error handling and user feedback mechanisms."

        return base_guidance

    def _setup_server_creation_handlers(self,
                                       server_name, server_description, language,
                                       template_type, features, ai_suggestions,
                                       generation_output, generate_btn,
                                       get_ai_help_btn, quick_database,
                                       quick_api, quick_ai):
        """Wire up event handlers for server creation."""

        # Generate server handler
        async def generate_server():
            try:
                if not server_name.value:
                    return "❌ Error: Server name is required"

                if not server_description.value:
                    return "❌ Error: Server description is required"

                # Create server configuration
                config = {
                    "name": server_name.value,
                    "description": server_description.value,
                    "language": language.value,
                    "template_type": template_type.value,
                    "features": features.value or []
                }

                # Generate the server
                result = await self._generate_server_async(config)
                return result

            except Exception as e:
                logger.error(f"Error generating server: {e}")
                return f"❌ Error: {str(e)}"

        # AI help handler
        def get_ai_help():
            try:
                context = {
                    "name": server_name.value or "unnamed_server",
                    "description": server_description.value or "No description provided",
                    "language": language.value,
                    "template_type": template_type.value,
                    "features": features.value or []
                }

                suggestions = self._generate_ai_suggestions(context)
                return suggestions

            except Exception as e:
                logger.error(f"Error getting AI help: {e}")
                return f"❌ Error getting suggestions: {str(e)}"

        # Quick template handlers
        def load_database_template():
            return (
                "database_server",
                "A database connector that provides tools for querying and managing data",
                "python",
                "database",
                ["tools", "resources"]
            )

        def load_api_template():
            return (
                "api_wrapper",
                "An API wrapper that exposes external API functionality to AI models",
                "python",
                "api",
                ["tools", "auth"]
            )

        def load_ai_template():
            return (
                "ai_agent",
                "An intelligent agent that can perform complex tasks using AI capabilities",
                "python",
                "ai_agent",
                ["tools", "prompts", "sampling"]
            )

        # Connect handlers
        generate_btn.click(
            fn=generate_server,
            outputs=generation_output
        )

        get_ai_help_btn.click(
            fn=get_ai_help,
            outputs=ai_suggestions
        )

        quick_database.click(
            fn=load_database_template,
            outputs=[server_name, server_description, language, template_type, features]
        )

        quick_api.click(
            fn=load_api_template,
            outputs=[server_name, server_description, language, template_type, features]
        )

        quick_ai.click(
            fn=load_ai_template,
            outputs=[server_name, server_description, language, template_type, features]
        )

    async def _generate_server_async(self, config: dict) -> str:
        """Generate server asynchronously."""
        try:
            # Ensure components are initialized
            if not self._initialized:
                await self.initialize()

            # Generate server using the server generator
            result = await self.server_generator.create_server(
                name=config["name"],
                description=config["description"],
                language=config["language"],
                template_type=config["template_type"],
                features=config["features"]
            )

            return f"✅ Server '{config['name']}' generated successfully!\n\n{result}\n\nNext steps:\n1. Navigate to the server directory\n2. Install dependencies\n3. Test the server with MCP client"

        except Exception as e:
            logger.error(f"Server generation failed: {e}")
            traceback.print_exc()
            return f"❌ Server generation failed: {str(e)}"

    def _generate_ai_suggestions(self, context: dict) -> str:
        """Generate AI suggestions based on current context."""
        try:
            suggestions = []

            # Basic validation suggestions
            if not context["name"] or context["name"] == "unnamed_server":
                suggestions.append("💡 Consider a more descriptive server name that reflects its purpose")

            if not context["description"] or context["description"] == "No description provided":
                suggestions.append("💡 Add a detailed description to generate better code")

            # Feature-specific suggestions
            features = context.get("features", [])

            if "tools" in features:
                suggestions.append("🔧 Tools selected: Your server will expose functions that AI can call")

            if "resources" in features:
                suggestions.append("📚 Resources selected: Your server will provide data sources for AI context")

            if "auth" in features:
                suggestions.append("🔐 Authentication selected: Consider what type of auth you need")

            # Template-specific suggestions
            template_type = context.get("template_type", "basic")

            if template_type == "database":
                suggestions.append("🗄️ Database template: Consider which database type and connection method")
            elif template_type == "api":
                suggestions.append("🌐 API template: Think about rate limiting and error handling")
            elif template_type == "ai_agent":
                suggestions.append("🧠 AI Agent template: Define the agent's capabilities and persona")

            if not suggestions:
                suggestions.append("✨ Your configuration looks good! Click 'Generate MCP Server' to create your server.")

            return "\n\n".join(suggestions)

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return "❌ Error generating suggestions. Please check your configuration."

    def _get_custom_css(self) -> str:
        """Custom CSS for enhanced visual appeal."""
        return """
        .gradio-container {
            font-family: 'Inter', sans-serif;
        }

        #create-tab, #templates-tab, #workflows-tab, #monitor-tab, #guidance-tab {
            padding: 20px;
        }

        .gr-button {
            border-radius: 8px;
            font-weight: 500;
        }

        .gr-textbox, .gr-dropdown {
            border-radius: 6px;
        }
        """


def launch_interface(
    port: int = 7860,
    share: bool = False,
    auth: tuple[str, str] | None = None
):
    """
    Launch the Gradio interface with sensible defaults.

    Args:
        port: Port to run the interface on
        share: Whether to create a public link
        auth: Optional (username, password) tuple for authentication
    """

    # Initialize the interface - create async handler
    interface_manager = MCPCreatorInterface()

    # Create interface first
    interface = interface_manager.create_interface()

    # Initialize components in background when interface loads
    def init_on_startup():
        try:
            # Try to run async initialization
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule as task
                    asyncio.create_task(interface_manager.initialize())
                else:
                    # If no loop, run new one
                    asyncio.run(interface_manager.initialize())
            except RuntimeError:
                # Fallback: create new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(interface_manager.initialize())

            logger.info("MCP Creator interface initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize interface: {e}")
            # Continue anyway - interface will work with limited functionality

    # Run initialization
    init_on_startup()

    interface.launch(
        server_port=port,
        share=share,
        auth=auth
    )


if __name__ == "__main__":
    # Load settings from environment
    settings = Settings()

    launch_interface(
        port=settings.gradio_server_port,
        share=settings.gradio_share
    )
