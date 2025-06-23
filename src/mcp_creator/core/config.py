"""Configuration management for MCP Creator."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Clean, centralized configuration management."""

    # Core paths
    output_dir: Path = Field(default=Path("./mcp_servers"), description="Default output directory")
    template_dir: Path = Field(default=Path("./templates"), description="Template directory")
    workflow_dir: Path = Field(default=Path("./mcp_creator_workflows"), description="Workflow storage directory")

    # AI provider settings
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    groq_api_key: str | None = Field(default=None, description="Groq API key")

    # Interface settings
    gradio_port: int = Field(default=7860, description="Gradio server port")
    gradio_share: bool = Field(default=False, description="Enable Gradio sharing")

    # Operational settings
    log_level: str = Field(default="INFO", description="Logging level")
    max_concurrent: int = Field(default=3, description="Max concurrent generations")
    enable_sandbox: bool = Field(default=True, description="Enable sandboxing")

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

    def __post_init__(self) -> None:
        """Ensure directories exist."""
        for path in [self.output_dir, self.template_dir, self.workflow_dir]:
            path.mkdir(parents=True, exist_ok=True)

    @property
    def has_ai_provider(self) -> bool:
        """Check if any AI provider is configured."""
        return any([
            self.anthropic_api_key,
            self.openai_api_key,
            self.groq_api_key,
        ])
