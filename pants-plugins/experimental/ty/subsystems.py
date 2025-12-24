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


class Ty(TemplatedExternalTool):
    options_scope = "ty"
    name = "Ty"
    help = softwrap("""An extremely fast Python type checker (https://github.com/astral-sh/ty).""")

    default_version = "0.0.2"
    default_known_versions = [
        "0.0.2|linux_arm64|a8a118e865a1d0665c4d6879585a87dc1f07492e8c18a2ba06a76df9f68df1fb|9212580",
        "0.0.2|linux_x86_64|ddb248a3b7f4fb99612dff94f76e3ab52e617e4c58dc933bd74b963853ee1902|9880518",
        "0.0.2|macos_arm64|dc3348dde593faa28b778cd51ce662b76b001d5eb83bf78415b04ec00f2db1b5|8755631",
        "0.0.2|macos_x86_64|98d4e920d616b5a3299a59392e18b76773ef5cb810f0c76d54b0a2e25b582966|9346271",
    ]

    default_url_template = (
        "https://github.com/astral-sh/ty/releases/download/{version}/ty-{platform}.tar.gz"
    )

    # TODO: Swap to musl, like Ruff?
    default_url_platform_mapping = {
        "linux_arm64": "aarch64-unknown-linux-gnu",
        "linux_x86_64": "x86_64-unknown-linux-gnu",
        "macos_arm64": "aarch64-apple-darwin",
        "macos_x86_64": "x86_64-apple-darwin",
    }

    def generate_exe(self, plat: Platform) -> str:
        return f"ty-{self.default_url_platform_mapping[plat.value]}/ty"

    skip = SkipOption("check")
    args = ArgsListOption(example="--version")

    _interpreter_constraints = StrListOption(
        advanced=True,
        default=["CPython>=3.8,<3.15"],
        help="Python interpreter constraints for Ty.",
    )

    @property
    def interpreter_constraints(self) -> InterpreterConstraints:
        """The interpreter constraints to use when installing and running the tool.

        This assumes you have set the class property `register_interpreter_constraints = True`.
        """
        return InterpreterConstraints(self._interpreter_constraints)

    def config_request(self) -> ConfigFilesRequest:
        """Ty will look for a `pyproject.toml` (with a `[tool.ty]` section) in the project root."""

        # TODO: Add support for ty.toml, and scanning parent directories
        # TODO: Should XDG config also be supported? Ty handles it - but that would make for non-reproducible results across systems
        return ConfigFilesRequest(
            discovery=True,
            check_content={"pyproject.toml": b"[tool.ty"},
        )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *Ty.rules(),
        UnionRule(ExportableTool, Ty),
    )
