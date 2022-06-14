from __future__ import annotations
from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.option.custom_types import shell_str
from pants.util.strutil import softwrap
from pants.option.option_types import ArgsListOption, SkipOption
from pants.util.docutil import git_url
from pants.backend.python.goals.export import ExportPythonTool, ExportPythonToolSentinel
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from typing import Iterable


class AnsibleLint(PythonToolBase):
    options_scope = "ansible-lint"
    name = "AnsibleLint"
    help = softwrap(
        """
        The ansible-lint utility for formatting Ansible playbooks, roles and collections (https://ansible-lint.readthedocs.io/en/latest/)."""
    )

    default_version = "ansible-lint==5.3.2"
    default_main = ConsoleScript("ansible-lint")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7,<4"]

    skip = SkipOption("fmt", "lint")
    args = ArgsListOption(example="-f pep8")

    register_lockfile = True
    default_lockfile_resource = (
        "pants.backend.ansible.lint.ansible_lint",
        "ansible_lint.lock",
    )
    default_lockfile_path = (
        "pants-plugins/experimental/ansible/lint/ansible_lint/ansible_lint.lock"
    )
    default_lockfile_url = git_url(default_lockfile_path)


class AnsibleLintExportSentinel(ExportPythonToolSentinel):
    pass


@rule
def ansible_lint_export(
    _: AnsibleLintExportSentinel, ansible_lint: AnsibleLint
) -> ExportPythonTool:
    return ExportPythonTool(
        resolve_name=ansible_lint.options_scope,
        pex_request=ansible_lint.to_pex_request(),
    )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        UnionRule(ExportPythonToolSentinel, AnsibleLintExportSentinel),
    )
