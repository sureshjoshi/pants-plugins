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
from pants.core.util_rules.external_tool import ExternalTool
from pants.option.option_types import ArgsListOption
from pants.util.logging import LogLevel


class SwiftSubsystem(Subsystem):
    options_scope = "swift"
    name = "swift"
    help = """The Swift programming language (https://www.swift.org/). 
    Compilation occurs via the underlying LLVM front-end. ie. "swift-frontend -frontend" 
    """

    args = ArgsListOption(example="-target x86_64-apple-macosx12.0")


@dataclass(frozen=True)
class SwiftToolchain:
    """A configured swift toolchain for the current platform."""

    exe: str
    # sdk: str #
    # target: str
    # linker_options: list[str] = []


@rule(desc="Setup the Swift Toolchain", level=LogLevel.DEBUG)
async def setup_swift_toolchain(swift: SwiftSubsystem) -> SwiftToolchain:
    default_search_paths = ["/usr/local/bin", "/usr/bin", "/bin"]
    swiftc_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name="swiftc",
            search_path=default_search_paths,
            test=BinaryPathTest(args=["--version"]),
        ),
    )
    if not swiftc_paths or not swiftc_paths.first_path:
        raise BinaryNotFoundError(
            f"Could not find 'swiftc' in any of {default_search_paths}."
        )

    return SwiftToolchain(exe=swiftc_paths.first_path.path)


def rules() -> Iterable[Rule | UnionRule]:
    return collect_rules()
