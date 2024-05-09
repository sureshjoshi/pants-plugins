# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable
from textwrap import dedent

import pytest
from experimental.ansible.lint.ansible_lint import rules as ansible_lint_rules
from experimental.ansible.lint.ansible_lint import skip_field
from experimental.ansible.lint.ansible_lint.rules import (
    AnsibleLintFieldSet,
    AnsibleLintRequest,
)

# from pants.backend.javascript.subsystems import nodejs
from experimental.ansible.target_types import AnsibleSourcesGeneratorTarget
from pants.backend.python import target_types_rules
from pants.core.goals.lint import LintResult, LintResults
from pants.core.util_rules import config_files, source_files
from pants.engine.addresses import Address
from pants.engine.fs import EMPTY_DIGEST
from pants.engine.target import Target
from pants.testutil.rule_runner import QueryRule, RuleRunner


@pytest.fixture
def rule_runner() -> RuleRunner:
    return RuleRunner(
        rules=[
            *ansible_lint_rules.rules(),
            *skip_field.rules(),
            *source_files.rules(),
            *config_files.rules(),
            *target_types_rules.rules(),
            QueryRule(LintResults, (AnsibleLintRequest,)),
        ],
        target_types=[AnsibleSourcesGeneratorTarget],
    )


EMPTY_PLAYBOOK = dedent(
    """\
    ---
    """
)

VALID_PLAYBOOK = dedent(
    """\
    ---
    - hosts: localhost
      tasks:
        - name: A do-nothing task that touches a tmp file
          ansible.builtin.file:
            path: /tmp/ansible-lint.pants
            state: touch
            mode: u=r,g=r,o=r
    """
)

ANSIBLE_LINT_CONFIG = dedent(
    """\
    ---
    exclude_paths:
      - playbook.yml
    """
)


def run_ansible_lint(
    rule_runner: RuleRunner,
    targets: Iterable[Target],
    *,
    extra_args: list[str] | None = None,
) -> tuple[LintResult, ...]:
    rule_runner.set_options(
        [
            "--backend-packages=['experimental.ansible', 'experimental.ansible.lint.ansible_lint']",
            *(extra_args or ()),
        ],
        env_inherit={"PATH", "PYENV_ROOT", "HOME"},
    )
    field_sets = [AnsibleLintFieldSet.create(tgt) for tgt in targets]
    lint_result = rule_runner.request(
        LintResults,
        [
            AnsibleLintRequest(field_sets),
        ],
    )
    return lint_result.results


def test_success(rule_runner: RuleRunner) -> None:
    rule_runner.write_files(
        {
            "playbook.yml": VALID_PLAYBOOK,
            "BUILD": "ansible_sources(name='t', sources=['playbook.yml'])",
        }
    )
    tgt = rule_runner.get_target(
        Address("", target_name="t", relative_file_path="playbook.yml")
    )
    lint_results = run_ansible_lint(
        rule_runner,
        [tgt],
    )
    assert len(lint_results) == 1
    assert lint_results[0].exit_code == 0
    assert lint_results[0].report == EMPTY_DIGEST


def test_failure(rule_runner: RuleRunner) -> None:
    rule_runner.write_files(
        {
            "playbook.yml": EMPTY_PLAYBOOK,
            "BUILD": "ansible_sources(name='t', sources=['playbook.yml'])",
        }
    )
    tgt = rule_runner.get_target(
        Address("", target_name="t", relative_file_path="playbook.yml")
    )
    lint_results = run_ansible_lint(
        rule_runner,
        [tgt],
    )
    assert len(lint_results) == 1
    assert lint_results[0].exit_code == 2
    assert lint_results[0].report == EMPTY_DIGEST
    assert "syntax-check: Empty playbook" in lint_results[0].stdout


def test_config(rule_runner: RuleRunner) -> None:
    rule_runner.write_files(
        {
            "playbook.yml": EMPTY_PLAYBOOK,
            ".ansible-lint": ANSIBLE_LINT_CONFIG,
            "BUILD": "ansible_sources(name='t', sources=['playbook.yml'])",
        }
    )
    tgt = rule_runner.get_target(
        Address("", target_name="t", relative_file_path="playbook.yml")
    )
    lint_results = run_ansible_lint(
        rule_runner,
        [tgt],
    )
    assert len(lint_results) == 1
    assert lint_results[0].exit_code == 0
    assert lint_results[0].report == EMPTY_DIGEST


def test_skip(rule_runner: RuleRunner) -> None:
    rule_runner.write_files(
        {
            "playbook.yml": VALID_PLAYBOOK,
            "BUILD": "ansible_sources(name='t',  sources=['**/*'])",
        }
    )
    tgt = rule_runner.get_target(
        Address("", target_name="t", relative_file_path="playbook.yml")
    )
    lint_result = run_ansible_lint(
        rule_runner, [tgt], extra_args=["--ansible-lint-skip"]
    )
    assert not lint_result
