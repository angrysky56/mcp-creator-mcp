"""Template management system with elegant abstractions."""

import json
import logging
from pathlib import Path
from typing import Any

import aiofiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import Settings

logger = logging.getLogger(__name__)


class Template:
    """Clean template representation with minimal cognitive overhead."""

    def __init__(self, name: str, path: Path, metadata: dict[str, Any]):
        self.name = name
        self.path = path
        self.metadata = metadata

    @property
    def description(self) -> str:
        return self.metadata.get("description", "No description")

    @property
    def language(self) -> str:
        return self.metadata.get("language", "unknown")

    @property
    def features(self) -> list[str]:
        return self.metadata.get("features", [])


class TemplateManager:
    """Elegant template management with predictable patterns."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.templates: dict[str, Template] = {}
        # Point FileSystemLoader to the languages directory where templates are organized by language
        languages_dir = settings.template_cache_dir / "languages"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(languages_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    async def initialize(self) -> None:
        """Load all templates with graceful error handling."""
        try:
            await self._discover_templates()
            logger.info(f"Loaded {len(self.templates)} templates")
        except Exception as e:
            logger.warning(f"Template initialization incomplete: {e}")

    async def list_templates(self, language: str | None = None) -> dict[str, list[dict]]:
        """list templates with optional language filtering."""
        result = {}

        for template in self.templates.values():
            if language and template.language != language:
                continue

            lang = template.language
            if lang not in result:
                result[lang] = []

            result[lang].append({
                "name": template.name,
                "description": template.description,
                "features": template.features,
            })

        return result

    async def get_template(self, name: str) -> Template | None:
        """Retrieve template by name with simple interface."""
        return self.templates.get(name)

    async def render_template(self, template_name: str, variables: dict[str, Any]) -> str:
        """Render template with variables, handling errors gracefully."""
        try:
            template = self.jinja_env.get_template(f"{template_name}/template.py.j2")
            return template.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise

    async def _discover_templates(self) -> None:
        """Discover and load template metadata."""
        # Use the updated settings field name for the base template directory
        base_template_dir = self.settings.template_cache_dir
        template_languages_dir = base_template_dir / "languages"

        if not template_languages_dir.exists():
            logger.warning(f"Template languages directory not found: {template_languages_dir}")
            return

        for lang_dir in template_languages_dir.iterdir(): # Updated variable name
            if not lang_dir.is_dir():
                continue

            for template_dir in lang_dir.iterdir():
                if not template_dir.is_dir():
                    continue

                await self._load_template(template_dir, lang_dir.name)

    async def _load_template(self, template_path: Path, language: str) -> None:
        """Load individual template with metadata."""
        metadata_file = template_path / "metadata.json"

        if not metadata_file.exists():
            # Create default metadata for templates without it
            metadata = {
                "name": template_path.name,
                "description": f"Template for {template_path.name}",
                "language": language,
                "features": [],
            }
        else:
            try:
                async with aiofiles.open(metadata_file) as f:
                    content = await f.read()
                    metadata = json.loads(content)
            except Exception as e:
                logger.warning(f"Invalid metadata in {metadata_file}: {e}")
                return

        template_key = f"{language}:{template_path.name}"
        self.templates[template_key] = Template(
            name=template_path.name,
            path=template_path,
            metadata=metadata,
        )

    async def cleanup(self) -> None:
        """Clean shutdown with resource cleanup."""
        self.templates.clear()
        logger.info("Template manager cleaned up")
