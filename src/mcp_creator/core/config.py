"""Configuration management for MCP Creator."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Clean, centralized configuration management."""

    # Core paths / Operational Settings from .env.example
    default_output_dir: Path = Field(default=Path("./mcp_servers"), description="Default output directory for generated servers")
    template_cache_dir: Path = Field(default=Path("./templates"), description="Directory for server templates")
    workflow_save_dir: Path = Field(default=Path("./mcp_creator_workflows"), description="Directory for saved workflows")
    log_level: str = Field(default="INFO", description="Logging level")

    # AI provider settings (though .env.example states client handles API keys)
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key, if server were to use it directly")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key, if server were to use it directly")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL, if server were to use it directly")
    groq_api_key: str | None = Field(default=None, description="Groq API key, if server were to use it directly")

    # Gradio Interface Settings
    gradio_server_port: int = Field(default=7860, description="Gradio server port")
    gradio_share: bool = Field(default=False, description="Enable Gradio sharing via ngrok")
    gradio_auth_enabled: bool = Field(default=False, description="Enable Gradio authentication")

    # Performance Settings
    max_concurrent_generations: int = Field(default=3, description="Max concurrent server generation tasks")
    template_update_check: bool = Field(default=True, description="Enable checking for template updates")
    workflow_backup_enabled: bool = Field(default=True, description="Enable automatic backup of workflows")

    # Security Settings
    enable_sandbox: bool = Field(default=True, description="Enable sandboxing for generated server (concept)")
    max_template_size_mb: int = Field(default=10, description="Maximum allowed template size in MB")
    max_workflow_duration_minutes: int = Field(default=30, description="Maximum allowed duration for a workflow execution")

    # Development Settings
    debug_mode: bool = Field(default=False, description="Enable debug mode with more verbose logging")
    verbose_logging: bool = Field(default=False, description="Enable verbose logging across modules")


    class Config:
        env_file = ".env"
        env_prefix = "" # Environment variables will be read directly (e.g., DEFAULT_OUTPUT_DIR)
        case_sensitive = False

    def __post_init__(self) -> None:
        """Ensure directories exist."""
        # Ensure core directories are created if they don't exist
        for path_attr in [self.default_output_dir, self.template_cache_dir, self.workflow_save_dir]:
            if isinstance(path_attr, Path):
                path_attr.mkdir(parents=True, exist_ok=True)
            else: # Should not happen with Path types, but good practice
                Path(str(path_attr)).mkdir(parents=True, exist_ok=True)


    @property
    def has_ai_provider(self) -> bool:
        """Check if any AI provider is configured."""
        return any([
            self.anthropic_api_key,
            self.openai_api_key,
            self.groq_api_key,
        ])
