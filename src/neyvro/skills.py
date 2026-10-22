from dataclasses import dataclass
from pathlib import Path

from .skill_library import discover


@dataclass(frozen=True)
class SkillContract:
    name: str
    description: str
    required_scopes: tuple[str, ...]
    destructive: bool = False


def _canonical_root() -> Path:
    return Path(__file__).resolve().parents[2] / "skills"


def canonical_contracts(root: str | Path | None = None) -> tuple[SkillContract, ...]:
    """Expose the canonical registry through the original foundation API."""
    skills = discover(root or _canonical_root())
    return tuple(SkillContract(skill.name, skill.description, skill.required_scopes) for skill in skills)


SKILLS: tuple[SkillContract, ...] = canonical_contracts()


def validate_catalog() -> None:
    canonical = canonical_contracts()
    if len(canonical) != 27 or len({skill.name for skill in canonical}) != 27:
        raise ValueError("skill catalog must contain 27 unique contracts")
    if any(not skill.name or not skill.description for skill in canonical):
        raise ValueError("every skill requires metadata and instructions")
