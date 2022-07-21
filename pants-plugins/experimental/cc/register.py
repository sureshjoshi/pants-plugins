# Copyright 2021 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Iterable

from experimental.cc.goals import check
from experimental.cc.subsystems import toolchain
from experimental.cc.util_rules import compile
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *check.rules(),
        *compile.rules(),
        *toolchain.rules(),
    )

