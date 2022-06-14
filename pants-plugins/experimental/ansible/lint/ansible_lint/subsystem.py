from __future__ import annotations

import os
from typing import Iterable

from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.option.custom_types import shell_str
from pants.util.strutil import softwrap
from pants.option.option_types import ArgsListOption, SkipOption
from pants.util.docutil import git_url
from pants.backend.python.goals.export import ExportPythonTool, ExportPythonToolSentinel
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.core.util_rules.config_files import ConfigFilesRequest


class AnsibleLint(PythonToolBase):
    options_scope = "ansible-lint"
    name = "AnsibleLint"
    help = softwrap(
        """
        The ansible-lint utility for formatting Ansible playbooks, roles and collections (https://ansible-lint.readthedocs.io/en/latest/)."""
    )

    default_version = "ansible-lint==6.3.0"
    default_main = ConsoleScript("ansible-lint")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7,<4"]

    skip = SkipOption("fmt", "lint")
    args = ArgsListOption(example="-f pep8")

    # register_lockfile = True
    # default_lockfile_resource = (
    #     "experimental.ansible.lint.ansible_lint",
    #     "ansible_lint.lock",
    # )
    # default_lockfile_path = (
    #     "pants-plugins/experimental/ansible/lint/ansible_lint/ansible_lint.lock"
    # )
    # default_lockfile_url = git_url(default_lockfile_path)

    def config_request(self, dirs: Iterable[str]) -> ConfigFilesRequest:
        """ansible-lint will use the closest configuration file to the file currently being formatted, so add all of them."""
        config_files = (
            ".ansible-lint",
            ".config/ansible-lint.yml",
        )
        check_existence = [
            os.path.join(d, file) for file in config_files for d in ("", *dirs)
        ]
        return ConfigFilesRequest(
            discovery=True,
            check_existence=check_existence,
        )


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
