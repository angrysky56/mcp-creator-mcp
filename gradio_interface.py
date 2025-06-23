"""
Gradio interface for MCP Creator with elegant, intuitive design.

Provides a clean, user-friendly interface for creating MCP servers without
requiring deep technical knowledge while maintaining full power for experts.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import gradio as gr

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
            theme=gr.themes.Soft(
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

                server_description = gr.Textarea(
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
            value="<p>Loading templates...</p>",
            label="Templates"
        )

        # Template details
        with gr.Row():
            template_details = gr.Textbox(
                label="Template Details",
                lines=10,
                interactive=False
            )

    def _create_workflows_tab(self):
        """Create workflow management interface."""

        gr.Markdown("### Workflow Management")
        gr.Markdown("Save and reuse creation patterns for consistent results")

        with gr.Row():
            with gr.Column():
                workflow_list = gr.Dropdown(
                    label="Saved Workflows",
                    choices=[],
                    interactive=True
                )

                workflow_description = gr.Textbox(
                    label="Description",
                    interactive=False,
                    lines=3
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
            interactive=True
        )

        with gr.Row():
            save_workflow_changes = gr.Button("💾 Save Changes", variant="primary")
            validate_workflow = gr.Button("✅ Validate", variant="secondary")

    def _create_monitoring_tab(self):
        """Create server monitoring interface."""

        gr.Markdown("### Generated Servers")
        gr.Markdown("Monitor and manage your created MCP servers")

        # Server list
        server_list = gr.Dataframe(
            headers=["Name", "Status", "Created", "Features", "Actions"],
            datatype=["str", "str", "str", "str", "str"],
            label="Your Servers",
            interactive=False
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
                    interactive=False
                )

            with gr.Column():
                server_logs = gr.Textbox(
                    label="Recent Logs",
                    lines=8,
                    interactive=False
                )

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

    def _setup_server_creation_handlers(self, *components):
        """Wire up event handlers for server creation."""
        # This would contain the actual event handler setup
        # For now, just a placeholder structure
        pass

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

    # Initialize the interface
    interface_manager = MCPCreatorInterface()

    # Run initialization in event loop
    asyncio.run(interface_manager.initialize())

    # Create and launch interface
    interface = interface_manager.create_interface()

    interface.launch(
        server_port=port,
        share=share,
        auth=auth,
        show_tips=True,
        enable_queue=True
    )


if __name__ == "__main__":
    # Load settings from environment
    settings = Settings()

    launch_interface(
        port=settings.gradio_port,
        share=settings.gradio_share
    )
