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

    default_version = "1.0.0"
    default_known_versions = [
        "1.0.0|linux_arm64|0f4a075b510c56089f672c7283528398656fd0a54110d6836919ce34dbf15c0b|12611542",
        "1.0.0|linux_x86_64|8b35318ba7377a621ff9d9ef77a443b6ad3cf065be566c84f5ae9c8318df5459|13141546",
        "1.0.0|macos_arm64|f3c2277245677b0128099f4971ae11c9c4a4d9a39aad70444c2f79a9d64b6893|12156236",
        "1.0.0|macos_x86_64|a152c7a775aa3088e7af5257330ba37d7d85337a0e85823b4dc2db556b7c39cf|12775069",
    ]

    default_url_template = (
        "https://github.com/facebook/pyrefly/releases/download/{version}/pyrefly-{platform}.tar.gz"
    )

    default_url_platform_mapping = {
        "linux_arm64": "linux-arm64",
        "linux_x86_64": "linux-x86_64",
        "macos_arm64": "macos-arm64",
        "macos_x86_64": "macos-x86_64",
    }

    def generate_exe(self, plat: Platform) -> str:
        return "pyrefly"

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
