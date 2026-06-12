# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable
from textwrap import dedent

import pytest  # pants: no-infer-dep

from experimental.pyrefly.register import rules as pyrefly_rules
from experimental.pyrefly.rules import PyreflyFieldSet, PyreflyRequest
from pants.backend.python import target_types_rules
from pants.backend.python.target_types import (
    PythonRequirementTarget,
    PythonSourcesGeneratorTarget,
    PythonSourceTarget,
)
from pants.core.goals.check import CheckResult, CheckResults
from pants.engine.addresses import Address
from pants.engine.rules import QueryRule
from pants.engine.target import Target
from pants.testutil.python_rule_runner import PythonRuleRunner

PACKAGE = "src/python/myapp"

GOOD_WITH_THIRDPARTY = dedent(
    """\
    import pydantic

    class Foo(pydantic.BaseModel):
        x: int
    """
)

BAD_FILE = dedent(
    """\
    x: int = "not-an-int"
    """
)

PYPROJECT_STRICT = dedent(
    """\
    [tool.pyrefly]
    python-version = "3.11"
    """
)

PYPROJECT = dedent(
    """\
    [tool.pyrefly]
    python-version = "3.11"
    permissive-ignores = true
    """
)


@pytest.fixture
def rule_runner() -> PythonRuleRunner:
    return PythonRuleRunner(
        rules=[
            *pyrefly_rules(),
            *target_types_rules.rules(),
            QueryRule(CheckResults, (PyreflyRequest,)),
        ],
        target_types=[
            PythonRequirementTarget,
            PythonSourcesGeneratorTarget,
            PythonSourceTarget,
        ],
    )


def run_pyrefly(
    rule_runner: PythonRuleRunner,
    targets: Iterable[Target],
    *,
    extra_args: Iterable[str] | None = None,
) -> tuple[CheckResult, ...]:
    rule_runner.set_options(
        [
            "--source-root-patterns=['src/python']",
            *(extra_args or ()),
        ],
        env_inherit={"PATH", "PYENV_ROOT", "HOME"},
    )
    result = rule_runner.request(
        CheckResults,
        [PyreflyRequest(PyreflyFieldSet.create(tgt) for tgt in targets)],
    )
    return result.results


def test_thirdparty_import_succeeds(rule_runner: PythonRuleRunner) -> None:
    """Minimal repro: third-party imports must resolve inside the sandbox.

    Without append_only_caches on the pyrefly Process, Pyrefly cannot query the
    requirements venv interpreter and reports spurious missing-import errors.
    """
    rule_runner.write_files(
        {
            "BUILD": "python_requirement(name='pydantic', requirements=['pydantic>=2,<3'])",
            "pyproject.toml": PYPROJECT,
            f"{PACKAGE}/main.py": GOOD_WITH_THIRDPARTY,
            f"{PACKAGE}/BUILD": "python_sources()",
        }
    )
    tgt = rule_runner.get_target(Address(PACKAGE, relative_file_path="main.py"))
    result = run_pyrefly(rule_runner, [tgt])
    assert len(result) == 1
    assert result[0].exit_code == 0
    output = f"{result[0].stdout}\n{result[0].stderr}"
    assert "missing-import" not in output.lower()
    assert "0 errors" in output.lower()


def test_type_error_fails(rule_runner: PythonRuleRunner) -> None:
    rule_runner.write_files(
        {
            "pyproject.toml": PYPROJECT_STRICT,
            f"{PACKAGE}/main.py": BAD_FILE,
            f"{PACKAGE}/BUILD": "python_sources()",
        }
    )
    tgt = rule_runner.get_target(Address(PACKAGE, relative_file_path="main.py"))
    result = run_pyrefly(rule_runner, [tgt])
    assert len(result) == 1
    assert result[0].exit_code == 1


def test_skip(rule_runner: PythonRuleRunner) -> None:
    rule_runner.write_files(
        {
            "BUILD": "python_requirement(name='pydantic', requirements=['pydantic>=2,<3'])",
            "pyproject.toml": PYPROJECT,
            f"{PACKAGE}/main.py": BAD_FILE,
            f"{PACKAGE}/BUILD": "python_sources()",
        }
    )
    tgt = rule_runner.get_target(Address(PACKAGE, relative_file_path="main.py"))
    result = run_pyrefly(rule_runner, [tgt], extra_args=["--pyrefly-skip"])
    assert not result
