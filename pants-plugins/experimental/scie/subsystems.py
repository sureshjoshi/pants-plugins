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

    default_version = "0.18.1"
    default_known_versions = [
        "0.18.1|linux_arm64|f2e813b0e72f1b1c291d58b39389a20128d475c8ca55d7ac0fbe2b2e16e58c6d|33079228",
        "0.18.1|linux_x86_64|18d43f10f908f8dc0332909ced3da172cb53c47676e35b882f815655c9d091e9|33201562",
        "0.18.1|macos_arm64|aa669262b3ff29f3ce223d58f6cf104f5639c97fdabb635b90ffc578b057980f|21706012",
        "0.18.1|macos_x86_64|8ee8729afe2ed5bd0be4cd1d0ee6232f44c0a98a30e8d1a90f4758e7085d84ac|21876565",
    ]

    default_url_template = (
        "https://github.com/a-scie/lift/releases/download/v{version}/science-fat-{platform}"
    )

    default_url_platform_mapping = {
        "linux_arm64": "musl-linux-aarch64",
        "linux_x86_64": "musl-linux-x86_64",
        "macos_arm64": "macos-aarch64",
        "macos_x86_64": "macos-x86_64",
    }

    # args = ArgsListOption(example="--release")


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *Science.rules(),  # type: ignore[call-arg]
    )
