# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Iterable

from pants.core.util_rules.external_tool import TemplatedExternalTool
from pants.engine.rules import Rule, collect_rules
from pants.engine.unions import UnionRule
from pants.util.strutil import softwrap


class ScieJump(TemplatedExternalTool):
    options_scope = "scie-jump"
    help = softwrap("""A Self Contained Interpreted Executable Launcher.""")

    default_version = "v0.10.0"
    default_known_versions = [
        "v0.10.0|linux_arm64|8d24647a8db9581200b3d2e9a863937b6160cf1a26e62f1dcbfad05bf93d7942|1446616",
        "v0.10.0|linux_x86_64|6dc9c7edd1f088b3a2718ee5740a9f9243516e5cd087557546f35af2e0a5fa8c|1692888",
        "v0.10.0|macos_arm64|b19511bb715aa948e221a53ad5be37945647be3c77bf06b85e0269cb1366b340|1367104",
        "v0.10.0|macos_x86_64|e1793daf1b253a5e7c1c445a3620099e4c1ae3424dd9095f9b1d6f1a5b14f325|1475176",
    ]

    default_url_template = (
        "https://github.com/a-scie/jump/releases/download/{version}/scie-jump-{platform}"
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
