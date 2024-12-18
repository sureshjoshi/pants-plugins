# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable

from pants.core.util_rules.external_tool import TemplatedExternalTool
from pants.engine.rules import Rule, collect_rules
from pants.engine.unions import UnionRule
from pants.util.strutil import softwrap


class Science(TemplatedExternalTool):
    options_scope = "science"
    help = softwrap("""A high level tool to build scies with.""")

    default_version = "0.9.0"
    default_known_versions = [
        "0.9.0|linux_arm64|c5fa67cf27f73c916c1422f33b11a8bf60ac0e49d477a53e2437c97a8dd23124|8626343",
        "0.9.0|linux_x86_64|d2d0288d74da9ca5423c8ec8e3afe78228fe25c9eb854c5901e14882af23d5b1|9949993",
        "0.9.0|macos_arm64|742d36790223b10577394f0f283afd91014fcb10cfab960de69a7e4f95100e83|4481336",
        "0.9.0|macos_x86_64|b5e1c6a18a782c65591e5a1149cd15592509c79227243e34cca09bebf2cb1942|4605864",
    ]

    default_url_template = (
        "https://github.com/a-scie/lift/releases/download/v{version}/science-{platform}"
    )

    default_url_platform_mapping = {
        "linux_arm64": "linux-aarch64",
        "linux_x86_64": "linux-x86_64",
        "macos_arm64": "macos-aarch64",
        "macos_x86_64": "macos-x86_64",
    }

    # args = ArgsListOption(example="--release")


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *Science.rules(),  # type: ignore[call-arg]
    )
