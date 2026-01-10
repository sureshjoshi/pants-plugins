# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable

from pants.backend.python.util_rules.interpreter_constraints import (
    InterpreterConstraints,
)
from pants.core.goals.resolves import ExportableTool
from pants.core.util_rules.config_files import ConfigFilesRequest
from pants.core.util_rules.external_tool import TemplatedExternalTool
from pants.engine.platform import Platform
from pants.engine.rules import Rule, collect_rules
from pants.engine.unions import UnionRule
from pants.option.option_types import ArgsListOption, SkipOption, StrListOption
from pants.util.strutil import softwrap


class Pyrefly(TemplatedExternalTool):
    options_scope = "pyrefly"
    name = "Pyrefly"
    help = softwrap("""A fast type checker and language server for Python (https://github.com/facebook/pyrefly).""")

    default_version = "0.47.0"
    default_known_versions = [
        "0.47.0|linux_arm64|ff64d8c6191f6199423b96e1f29a9d52405fad49347880af7f9d1559c51176d3|112163992",
        "0.47.0|linux_x86_64|0a84a30753622c0f988bbc650fe6e6307df57986cba1afea2e67e1d8c2e989fc|113266536",
        "0.47.0|macos_arm64|494934686a7ecc2e589407bf8979795272aa8eb68abfea06f3643d6422d6ecce|22188776",
        "0.47.0|macos_x86_64|e1d38aa61bcc4df1b9a1036db2b94ab24e24fbac53f674ef2b8e2ec326246d62|23746832",
    ]

    # TODO: Pyrefly only releases to PyPi
    # TODO: https://github.com/facebook/pyrefly/issues/883
    # Pulling from my super temporary repo... Uncompressed binaries - the Linux ones are > 100MB !?!?
    default_url_template = (
        "https://github.com/sureshjoshi/pyrefly-binaries/releases/download/{version}/pyrefly-{platform}"
    )

    default_url_platform_mapping = {
        "linux_arm64": "linux-arm64",
        "linux_x86_64": "linux-x86_64",
        "macos_arm64": "macos-arm64",
        "macos_x86_64": "macos-x86_64",
    }

    def generate_exe(self, plat: Platform) -> str:
        return f"pyrefly-{self.default_url_platform_mapping[plat.value]}"

    skip = SkipOption("check")
    args = ArgsListOption(example="--version")

    _interpreter_constraints = StrListOption(
        advanced=True,
        default=["CPython>=3.8,<3.15"],
        help="Python interpreter constraints for Pyrefly.",
    )

    @property
    def interpreter_constraints(self) -> InterpreterConstraints:
        """The interpreter constraints to use when installing and running the tool.

        This assumes you have set the class property `register_interpreter_constraints = True`.
        """
        return InterpreterConstraints(self._interpreter_constraints)

    def config_request(self) -> ConfigFilesRequest:
        """Pyrefly will look for a `pyproject.toml` (with a `[tool.pyrefly]` section) in the project root."""

        # TODO: Add support for pyrefly.toml, and scanning parent directories
        return ConfigFilesRequest(
            discovery=True,
            check_content={"pyproject.toml": b"[tool.pyrefly"},
        )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *Pyrefly.rules(),
        UnionRule(ExportableTool, Pyrefly),
    )
