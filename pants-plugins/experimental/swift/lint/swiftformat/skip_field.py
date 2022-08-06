# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Iterable

from experimental.swift.target_types import SwiftSourcesGeneratorTarget, SwiftSourceTarget
from pants.engine.rules import Rule
from pants.engine.target import BoolField
from pants.engine.unions import UnionRule


class SkipSwiftFormatField(BoolField):
    alias = "skip_swift_format"
    default = False
    help = "If true, don't run swift-format on this target's code."


def rules() -> Iterable[Rule | UnionRule]:
    return (
        SwiftSourcesGeneratorTarget.register_plugin_field(SkipSwiftFormatField),
        SwiftSourceTarget.register_plugin_field(SkipSwiftFormatField),
    )
