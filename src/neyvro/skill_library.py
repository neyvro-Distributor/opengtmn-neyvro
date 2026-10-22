"""Canonical Agent Skills registry, validation, loading, search, and builds."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - the declared dependency is installed in normal use.
    yaml = None


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n?", re.DOTALL)
RELATIVE_LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:sk|rk|ghp|github_pat)_[A-Za-z0-9_\-]{16,}\b"),
    re.compile(r"(?i)\b(?:password|client_secret|api_key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    version: str
    maturity: str
    mode: str
    required_scopes: tuple[str, ...]
    related_skills: tuple[str, ...]
    path: str
    markdown: str

    def index_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "maturity": self.maturity,
            "mode": self.mode,
            "required_scopes": list(self.required_scopes),
            "related_skills": list(self.related_skills),
            "path": self.path,
        }


class SkillValidationError(ValueError):
    """Raised when a canonical skill library violates its contract."""


def _frontmatter(text: str, source: Path) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise SkillValidationError(f"{source}: missing YAML frontmatter")
    if yaml is None:
        raise SkillValidationError("PyYAML is required to parse skill frontmatter")
    data = yaml.safe_load(match.group("body"))
    if not isinstance(data, dict):
        raise SkillValidationError(f"{source}: frontmatter must be a YAML mapping")
    return data


def _string_list(value: Any, field: str, source: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise SkillValidationError(f"{source}: {field} must be a string list")


def _read_skill(path: Path, root: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    data = _frontmatter(text, path)
    required = ("name", "description")
    missing = [field for field in required if not isinstance(data.get(field), str) or not data[field].strip()]
    if missing:
        raise SkillValidationError(f"{path}: missing required field(s): {', '.join(missing)}")
    name = data["name"].strip()
    description = data["description"].strip()
    if path.parent.name != name:
        raise SkillValidationError(f"{path}: name {name!r} does not match directory {path.parent.name!r}")
    if not NAME_RE.fullmatch(name):
        raise SkillValidationError(f"{path}: name must be lowercase kebab-case")
    if len(description) > 1024:
        raise SkillValidationError(f"{path}: description exceeds 1024 characters")
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    def field(name: str, default: Any = None) -> Any:
        return data[name] if name in data else metadata.get(name, default)

    version = str(field("version", "0.1.0"))
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SkillValidationError(f"{path}: version must use semantic versioning")
    maturity = str(field("maturity", "contract"))
    if maturity not in {"contract", "playbook", "verified"}:
        raise SkillValidationError(f"{path}: unsupported maturity {maturity!r}")
    mode = str(field("mode", "knowledge"))
    if mode not in {"knowledge", "research", "draft", "execution"}:
        raise SkillValidationError(f"{path}: unsupported mode {mode!r}")
    relative = path.relative_to(root).as_posix()
    return Skill(
        name=name,
        description=description,
        version=version,
        maturity=maturity,
        mode=mode,
        required_scopes=_string_list(field("required_scopes"), "required_scopes", path),
        related_skills=_string_list(field("related_skills"), "related_skills", path),
        path=relative,
        markdown=text,
    )


def discover(root: str | Path = "skills") -> tuple[Skill, ...]:
    """Load canonical skills in deterministic name order."""
    root = Path(root)
    if not root.is_dir():
        raise SkillValidationError(f"skill directory not found: {root}")
    skills = [_read_skill(path, root) for path in sorted(root.glob("*/SKILL.md"))]
    names = [skill.name for skill in skills]
    if len(names) != len(set(names)):
        raise SkillValidationError("duplicate skill names detected")
    known = set(names)
    for skill in skills:
        missing = sorted(set(skill.related_skills) - known)
        if missing:
            raise SkillValidationError(f"{skill.path}: unknown related skill(s): {', '.join(missing)}")
    return tuple(skills)


def validate(root: str | Path = "skills") -> list[str]:
    """Return all validation errors without hiding any invalid file."""
    root = Path(root)
    errors: list[str] = []
    if not root.is_dir():
        return [f"skill directory not found: {root}"]
    paths = sorted(root.glob("*/SKILL.md"))
    expected_dirs = sorted(path.parent.name for path in paths)
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        if not (directory / "SKILL.md").is_file():
            errors.append(f"{directory}: missing SKILL.md")
    loaded: list[Skill] = []
    for path in paths:
        try:
            loaded.append(_read_skill(path, root))
        except (OSError, SkillValidationError, ValueError) as exc:
            errors.append(str(exc))
    names = [skill.name for skill in loaded]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    errors.extend(f"duplicate skill name: {name}" for name in duplicates)
    known = set(names)
    for skill in loaded:
        for related in skill.related_skills:
            if related not in known:
                errors.append(f"{skill.path}: related skill not found: {related}")
        for target in RELATIVE_LINK_RE.findall(skill.markdown):
            target = target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (root / Path(skill.path).parent / target).resolve().exists():
                errors.append(f"{skill.path}: broken relative reference: {target}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(skill.markdown):
                errors.append(f"{skill.path}: credential-like content detected")
                break
    return errors


def load(name: str, root: str | Path = "skills") -> Skill:
    """Load one exact skill identifier; partial matches are rejected."""
    skills = {skill.name: skill for skill in discover(root)}
    try:
        return skills[name]
    except KeyError as exc:
        raise KeyError(f"unknown skill {name!r}") from exc


def search(query: str, root: str | Path = "skills") -> list[tuple[Skill, int]]:
    """Search metadata and Markdown content, returning deterministic scores."""
    terms = [term.casefold() for term in query.split() if term.strip()]
    if not terms:
        raise ValueError("search query cannot be empty")
    results: list[tuple[Skill, int]] = []
    for skill in discover(root):
        metadata = " ".join((skill.name, skill.description, skill.mode, *skill.related_skills)).casefold()
        body = skill.markdown.casefold()
        score = sum((3 if term in metadata else 0) + (1 if term in body else 0) for term in terms)
        if score:
            results.append((skill, score))
    return sorted(results, key=lambda item: (-item[1], item[0].name))


def build(root: str | Path = "skills", output_dir: str | Path = ".") -> dict[str, str]:
    """Build deterministic index, discovery file, and consolidated bundle."""
    skills = discover(root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = {
        "name": "neyvro-skills",
        "format": "Agent Skills (SKILL.md)",
        "version": "0.1.0",
        "source": "Neyvro",
        "count": len(skills),
        "skills": [skill.index_record() for skill in skills],
    }
    index_text = json.dumps(index, indent=2, sort_keys=False) + "\n"
    llms = "# Neyvro Agent Skills\n\n"
    llms += "Portable, on-demand skills for Neyvro-compatible AI agents.\n\n## Skills\n"
    for skill in skills:
        llms += f"- [{skill.name}]({skill.path}): {skill.description}\n"
    llms += "\n## Loading\n\nUse metadata discovery first, then load one exact `SKILL.md`; do not inject the whole bundle into every request.\n"
    bundle = "# Neyvro Agent Skills Bundle\n\nThis generated bundle is for explicit bulk import. Prefer registry discovery and on-demand loading in normal agent requests.\n\n"
    for skill in skills:
        bundle += f"\n---\n\n<!-- {skill.path} version {skill.version} -->\n\n{skill.markdown.rstrip()}\n"
    files = {
        "index.json": index_text,
        "llms.txt": llms,
        "dist/neyvro-skills.md": bundle,
    }
    for relative, content in files.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return files


def deterministic_build(root: str | Path = "skills", output_dir: str | Path = ".") -> bool:
    """Return whether a second build produces byte-identical artifacts."""
    first = build(root, output_dir)
    second = build(root, output_dir)
    return first == second
