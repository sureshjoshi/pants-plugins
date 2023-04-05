# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Iterable

from pants.core.util_rules.external_tool import TemplatedExternalTool
from pants.engine.rules import Rule, collect_rules
from pants.engine.unions import UnionRule
from pants.util.strutil import softwrap


class Science(TemplatedExternalTool):
    options_scope = "science"
    help = softwrap("""A high level tool to build scies with.""")

    default_version = "0.1.0"
    default_known_versions = [
        "0.1.0|linux_arm64|ecb4c8d7d882df2a7c15b9960765b2acb6bdb52e6c65bc2a94b6ce53196ba34c|6692875",
        "0.1.0|linux_x86_64|ea76ca3475275fd0a7c7fa8437b487f4de193a62c99eb88d9280d597265c6849|7575320",
        "0.1.0|macos_arm64|5041ecbdcccd61417a01668b33be58a085b0ec84519c6de37b9fec021f8fddb2|4557956",
        "0.1.0|macos_x86_64|3fcfba52d7a92dbdd93fb61ef3fd412e66e85249e9d2acb2259d4d104bf10aaa|4692688",
    ]

    default_url_template = (
        "https://github.com/a-scie/jump/releases/download/{version}/science-{platform}"
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
        *ScieJump.rules(),  # type: ignore[call-arg]
    )
