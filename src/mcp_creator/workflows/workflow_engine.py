"""Workflow engine with elegant abstractions for reusable creation patterns."""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

import aiofiles

from ..core.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single workflow step with clear interface."""

    id: str
    type: str  # 'input', 'ai_guidance', 'template_selection', 'generation'
    config: dict[str, Any]
    dependencies: list[str] | None = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class Workflow:
    """Clean workflow representation with serialization."""

    name: str
    description: str
    steps: list[WorkflowStep]
    version: str = "1.0.0"
    created_at: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Workflow':
        """Create workflow from dictionary."""
        steps = [WorkflowStep(**step) for step in data.get('steps', [])]
        return cls(
            name=data['name'],
            description=data['description'],
            steps=steps,
            version=data.get('version', '1.0.0'),
            created_at=data.get('created_at'),
            metadata=data.get('metadata', {}),
        )


class WorkflowEngine:
    """Elegant workflow management with predictable patterns."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.workflows: dict[str, Workflow] = {}

    async def initialize(self) -> None:
        """Load existing workflows with graceful error handling."""
        try:
            await self._load_workflows()
            await self._ensure_example_workflows()
            logger.info(f"Loaded {len(self.workflows)} workflows")
        except Exception as e:
            logger.warning(f"Workflow initialization incomplete: {e}")

    async def save_workflow(
        self,
        name: str,
        description: str,
        steps: list[dict[str, Any]],
    ) -> str:
        """Save workflow with automatic ID generation."""
        workflow_id = str(uuid4())[:8]

        # Convert step dictionaries to WorkflowStep objects
        workflow_steps = [WorkflowStep(**step) for step in steps]

        workflow = Workflow(
            name=name,
            description=description,
            steps=workflow_steps,
        )

        # Save to memory and disk
        self.workflows[workflow_id] = workflow
        await self._persist_workflow(workflow_id, workflow)

        logger.info(f"Saved workflow: {name} ({workflow_id})")
        return workflow_id

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Retrieve workflow by ID."""
        return self.workflows.get(workflow_id)

    async def list_workflows(self) -> dict[str, dict[str, str]]:
        """list all workflows with summary information."""
        return {
            workflow_id: {
                "name": workflow.name,
                "description": workflow.description,
                "created_at": workflow.created_at or "unknown",
                "steps": str(len(workflow.steps)),
            }
            for workflow_id, workflow in self.workflows.items()
        }

    async def execute_workflow(
        self,
        workflow_id: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute workflow with dependency resolution."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        try:
            return await self._execute_steps(workflow, inputs)
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    async def _execute_steps(
        self,
        workflow: Workflow,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute workflow steps with dependency resolution."""
        results = {}
        completed = set()

        # Simple execution order (could be enhanced with topological sort)
        for step in workflow.steps:
            if self._dependencies_met(step, completed):
                result = await self._execute_step(step, inputs, results)
                results[step.id] = result
                completed.add(step.id)

        return results

    def _dependencies_met(self, step: WorkflowStep, completed: set) -> bool:
        """Check if step dependencies are satisfied."""
        dependencies = step.dependencies if step.dependencies is not None else []
        return all(dep in completed for dep in dependencies)

    async def _execute_step(
        self,
        step: WorkflowStep,
        inputs: dict[str, Any],
        previous_results: dict[str, Any],
    ) -> Any:
        """Execute individual workflow step."""
        # This would be expanded with actual step execution logic
        logger.info(f"Executing step: {step.id} ({step.type})")

        if step.type == "input":
            return inputs.get(step.id, step.config.get("default"))
        elif step.type == "template_selection":
            return step.config.get("template", "basic")
        elif step.type == "ai_guidance":
            return "AI guidance placeholder"
        elif step.type == "generation":
            return "Generation complete"

        return f"Step {step.id} executed"

    async def _load_workflows(self) -> None:
        """Load workflows from disk."""
        workflow_dir = self.settings.workflow_dir

        if not workflow_dir.exists():
            return

        for workflow_file in workflow_dir.glob("*.json"):
            try:
                async with aiofiles.open(workflow_file) as f:
                    content = await f.read()
                    data = json.loads(content)

                workflow = Workflow.from_dict(data)
                workflow_id = workflow_file.stem
                self.workflows[workflow_id] = workflow

            except Exception as e:
                logger.warning(f"Failed to load workflow {workflow_file}: {e}")

    async def _persist_workflow(self, workflow_id: str, workflow: Workflow) -> None:
        """Save workflow to disk."""
        workflow_file = self.settings.workflow_dir / f"{workflow_id}.json"

        async with aiofiles.open(workflow_file, "w") as f:
            content = json.dumps(workflow.to_dict(), indent=2)
            await f.write(content)

    async def _ensure_example_workflows(self) -> None:
        """Create example workflows if none exist."""
        if self.workflows:
            return

        # Create a simple example workflow
        example_workflow = Workflow(
            name="Basic MCP Server",
            description="Create a basic MCP server with tools and resources",
            steps=[
                WorkflowStep(
                    id="collect_info",
                    type="input",
                    config={
                        "fields": ["name", "description", "features"],
                        "required": ["name", "description"],
                    },
                ),
                WorkflowStep(
                    id="select_template",
                    type="template_selection",
                    config={"template": "python:basic"},
                    dependencies=["collect_info"],
                ),
                WorkflowStep(
                    id="generate_server",
                    type="generation",
                    config={"language": "python"},
                    dependencies=["collect_info", "select_template"],
                ),
            ],
        )

        workflow_id = "example_basic"
        self.workflows[workflow_id] = example_workflow
        await self._persist_workflow(workflow_id, example_workflow)

    async def cleanup(self) -> None:
        """Clean shutdown."""
        self.workflows.clear()
        logger.info("Workflow engine cleaned up")
