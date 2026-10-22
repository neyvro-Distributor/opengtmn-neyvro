"""Local knowledge-only MCP server for the canonical Neyvro skill library.

The protocol implementation is provided by the official Python MCP SDK. This
module exposes only metadata and the exact contents of ``skills/*/SKILL.md``;
it has no customer-data or execution-service connection.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .skill_library import Skill, SkillValidationError, discover, load, search

LOGGER = logging.getLogger("neyvro.mcp.skills")
SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"
MAX_RESOURCE_BYTES = 256 * 1024
MAX_RESULTS = 100
SERVER_NAME = "neyvro-local-skills"

mcp = FastMCP(
    SERVER_NAME,
    instructions="Knowledge-only access to the portable Neyvro Agent Skills library. No customer records or execution tools are exposed.",
    log_level="WARNING",
)


def _catalog() -> tuple[Skill, ...]:
    return discover(SKILLS_ROOT)


def _bounded_content(skill: Skill) -> str:
    content = skill.markdown
    if len(content.encode("utf-8")) > MAX_RESOURCE_BYTES:
        raise ValueError(f"skill resource exceeds the {MAX_RESOURCE_BYTES}-byte limit")
    return content


def _public_metadata(skill: Skill) -> dict[str, Any]:
    # Deliberately omit the local filesystem path from the MCP surface.
    return {
        "name": skill.name,
        "description": skill.description,
        "version": skill.version,
        "maturity": skill.maturity,
        "mode": skill.mode,
        "required_scopes": list(skill.required_scopes),
        "related_skills": list(skill.related_skills),
        "resource_uri": f"neyvro://skills/{skill.name}",
    }


def _title(skill: Skill) -> str:
    return skill.name.replace("-", " ").title()


@mcp.tool(name="neyvro_list_skills", description="List public Neyvro skill metadata without exposing filesystem paths or customer records.")
def neyvro_list_skills(query: str | None = None, limit: int = MAX_RESULTS) -> list[dict[str, Any]]:
    """List skills, optionally filtering metadata and content by a query."""
    if limit < 1 or limit > MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}")
    skills = _catalog()
    if query is not None:
        if not query.strip():
            raise ValueError("query must not be empty when supplied")
        skills = tuple(item for item, _score in search(query, SKILLS_ROOT))
    return [_public_metadata(skill) for skill in skills[:limit]]


@mcp.tool(name="neyvro_get_skill", description="Get one exact public Neyvro skill and its original SKILL.md content.")
def neyvro_get_skill(name: str) -> dict[str, Any]:
    """Load one exact kebab-case skill identifier from the fixed registry."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name is required")
    skill = load(name, SKILLS_ROOT)
    return {**_public_metadata(skill), "content": _bounded_content(skill)}


@mcp.tool(name="neyvro_search_skills", description="Search public Neyvro skill metadata and content with deterministic relevance scores.")
def neyvro_search_skills(query: str, limit: int = MAX_RESULTS) -> list[dict[str, Any]]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")
    if limit < 1 or limit > MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}")
    return [{**_public_metadata(skill), "score": score} for skill, score in search(query, SKILLS_ROOT)[:limit]]


def _register_resources_and_prompts() -> None:
    """Register deterministic resources/prompts once at module initialization."""
    def make_resource(selected: str):
        def read_skill() -> str:
            return _bounded_content(load(selected, SKILLS_ROOT))

        read_skill.__name__ = f"read_{selected.replace('-', '_')}"
        return read_skill

    def make_prompt(selected: str, title: str, description: str):
        def workflow_prompt() -> str:
            return (
                f"Use the public Neyvro skill '{selected}' ({title}).\n\n"
                f"Activation guidance: {description}\n\n"
                "Load the exact skill resource when its workflow applies. Keep the work knowledge-only unless a separate authorized Neyvro execution service is explicitly available."
            )

        workflow_prompt.__name__ = f"prompt_{selected.replace('-', '_')}"
        return workflow_prompt

    for skill in _catalog():
        selected_name = skill.name
        selected_title = _title(skill)
        selected_description = skill.description
        resource_uri = f"neyvro://skills/{selected_name}"
        mcp.resource(
            resource_uri,
            name=selected_name,
            title=selected_title,
            description=selected_description,
            mime_type="text/markdown",
        )(make_resource(selected_name))
        mcp.prompt(
            name=selected_name,
            title=selected_title,
            description=selected_description,
        )(make_prompt(selected_name, selected_title, selected_description))


try:
    _register_resources_and_prompts()
except (OSError, SkillValidationError, ValueError) as exc:  # pragma: no cover - startup failure is exercised by CLI smoke tests.
    LOGGER.error("unable to register Neyvro skills: %s", exc)
    raise


def main() -> None:
    """Run the official SDK's stdio transport; protocol traffic owns stdout."""
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    mcp.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
