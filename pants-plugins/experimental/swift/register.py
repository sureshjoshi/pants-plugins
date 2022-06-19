# Copyright 2021 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Iterable

from experimental.swift.goals import check, tailor
from experimental.swift.subsystems import toolchain
from experimental.swift.target_types import (
    SwiftBinaryTarget,
    SwiftSourcesGeneratorTarget,
    SwiftSourceTarget,
)
from experimental.swift.util_rules import compile
from pants.engine.rules import Rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *check.rules(),
        *compile.rules(),
        *tailor.rules(),
        *toolchain.rules(),
    )


def target_types() -> Iterable[type[Target]]:
    return (SwiftSourceTarget, SwiftSourcesGeneratorTarget, SwiftBinaryTarget)
