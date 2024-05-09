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

    default_version = "0.3.4"
    default_known_versions = [
        "0.3.4|linux_arm64|9d30ffffee826f52a69c056fcb7c5e9a25d48980c573066cf64dd7f987c13b66|8578528",
        "0.3.4|linux_x86_64|926791a2243446711ed84b5465aa3786eed3c90d1654dd86ea82498fd5fcd4a2|9728714",
        "0.3.4|macos_arm64|d1e6eefd9bc89f2edb39775435ee25ad7fd5b158431561ac6fbbbf1552f855c0|4303745",
        "0.3.4|macos_x86_64|c3012fdd237a918db378bc215ec985aca0f26f42e8e4c80066032da94322897a|4502350",
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
