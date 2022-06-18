# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from pants.core.util_rules.system_binaries import (
    BinaryNotFoundError,
    BinaryPathRequest,
    BinaryPaths,
    BinaryPathTest,
)
from pants.engine.internals.selectors import Get
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.option.subsystem import Subsystem
from pants.util.logging import LogLevel


class SwiftcSubsystem(Subsystem):
    options_scope = "swiftc"
    name = "swiftc"
    help = "The Swift programming language (https://www.swift.org/)."


@dataclass(frozen=True)
class Swiftc:
    """Path to the swiftc installation."""

    path: str


@rule(desc="Find swiftc binary", level=LogLevel.DEBUG)
async def find_swiftc() -> Swiftc:
    default_search_paths = ["/usr/local/bin", "/usr/bin", "/bin"]
    swiftc_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name="swiftc",
            search_path=default_search_paths,
            test=BinaryPathTest(args=["--version"]),
        ),
    )
    if not swiftc_paths:
        raise BinaryNotFoundError(
            f"Could not find 'swiftc' in any of {default_search_paths}."
        )

    swiftc_bin = swiftc_paths.first_path
    return Swiftc(swiftc_bin)


def rules() -> Iterable[Rule | UnionRule]:
    return collect_rules()
