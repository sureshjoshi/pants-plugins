
# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from textwrap import dedent

import pytest

from experimental.ansible.lint.ansible_lint import rules as ansible_lint_rules
from experimental.ansible.lint.ansible_lint import skip_field
from experimental.ansible.lint.ansible_lint.rules import AnsibleLintFieldSet, AnsibleLintRequest
# from pants.backend.javascript.subsystems import nodejs
from experimental.ansible.target_types import AnsibleSourcesGeneratorTarget
from pants.backend.python import target_types_rules
from pants.core.goals.lint import LintTargetsRequest, LintResults
from pants.core.util_rules import config_files, source_files
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.addresses import Address
from pants.engine.fs import CreateDigest, Digest, FileContent, Snapshot
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
            QueryRule(SourceFiles, (SourceFilesRequest,)),
        ],
        target_types=[AnsibleSourcesGeneratorTarget],
    )

UNLINTED_FILE = dedent(
    """\
    ---
    -hosts:localhost
     roles:
     - role: example
    """
)

DEFAULT_LINTED_FILE = dedent(
    """\
    ---
    - hosts: localhost
        roles:
            - role: example
    """
)

def run_ansible_lint(
    rule_runner: RuleRunner,
    targets: list[Target],
    *,
    extra_args: list[str] | None = None,
) -> LintTargetsRequest:
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
    return lint_result

# def test_success_on_linted_file(rule_runner: RuleRunner) -> None:
#     rule_runner.write_files(
#         {"playbook.yml": DEFAULT_LINTED_FILE, "BUILD": "ansible_sources(name='t')"}
#     )
#     tgt = rule_runner.get_target(Address("", target_name="t", relative_file_path="main.js"))
#     lint_result = run_ansible_lint(
#         rule_runner,
#         [tgt],
#     )
#     assert fmt_result.output == get_snapshot(rule_runner, {"main.js": DEFAULT_FORMATTED_FILE})
#     assert lint_result.did_change is False

# def test_config(rule_runner: RuleRunner) -> None:
#     rule_runner.write_files(
#         {
#             "main.js": UNFORMATTED_FILE,
#             ".prettierrc": PRETTIERRC_FILE,
#             "BUILD": "javascript_sources(name='t')",
#         }
#     )
#     tgt = rule_runner.get_target(Address("", target_name="t", relative_file_path="main.js"))
#     fmt_result = run_prettier(
#         rule_runner,
#         [tgt],
#     )
#     assert fmt_result.skipped is False
#     assert fmt_result.output == get_snapshot(rule_runner, {"main.js": CONFIG_FORMATTED_FILE})
#     assert fmt_result.did_change is True

def test_skip(rule_runner: RuleRunner) -> None:
    rule_runner.write_files({"playbook.yml": DEFAULT_LINTED_FILE, "BUILD": "ansible_sources(name='t',  sources=['**/*'])"})
    tgt = rule_runner.get_target(Address("", target_name="t", relative_file_path="playbook.yml"))
    lint_result = run_ansible_lint(rule_runner, [tgt], extra_args=["--ansible-lint-skip"])
    assert lint_result.skipped is True