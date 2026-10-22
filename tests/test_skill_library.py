import json
from pathlib import Path

import pytest

from neyvro.skill_library import build, discover, load, search, validate


ROOT = Path(__file__).parents[1]
SKILLS = ROOT / "skills"


def test_canonical_library_has_expected_27_skills() -> None:
    skills = discover(SKILLS)
    assert len(skills) == 27
    assert len({skill.name for skill in skills}) == 27
    assert all(len(skill.version.split(".")) == 3 for skill in skills)


def test_validation_is_clean_and_related_references_resolve() -> None:
    assert validate(SKILLS) == []


def test_exact_loading_rejects_partial_identifiers() -> None:
    assert load("account-research", SKILLS).name == "account-research"
    with pytest.raises(KeyError):
        load("account", SKILLS)


def test_search_uses_metadata_and_content() -> None:
    results = search("evidence buyer", SKILLS)
    assert results
    assert results[0][0].name in {"evidence", "buyer-matching", "account-research"}


def test_build_is_deterministic(tmp_path: Path) -> None:
    first = build(SKILLS, tmp_path)
    second = build(SKILLS, tmp_path)
    assert first == second
    assert json.loads((tmp_path / "index.json").read_text())['count'] == 27
    assert (tmp_path / "dist/neyvro-skills.md").is_file()


def test_fixture_validation_catches_missing_description() -> None:
    fixture = ROOT / "tests/fixtures/skills/invalid-missing-description"
    errors = validate(fixture.parent)
    assert any("missing required field" in error for error in errors)


def test_fixture_loads_without_login() -> None:
    fixture_root = ROOT / "tests/fixtures/valid-library"
    assert load("valid-example", fixture_root).markdown.startswith("---")
