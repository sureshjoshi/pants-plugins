# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable

from pants.backend.python.target_types import (
    PythonSourcesGeneratorTarget,
    PythonSourceTarget,
    PythonTestsGeneratorTarget,
    PythonTestTarget,
    PythonTestUtilsGeneratorTarget,
)
from pants.engine.rules import Rule
from pants.engine.target import BoolField
from pants.engine.unions import UnionRule


class SkipTyField(BoolField):
    alias = "skip_ty"
    default = False
    help = "If true, don't run Ty on this target's code."


def rules() -> Iterable[Rule | UnionRule]:
    return (
        PythonSourcesGeneratorTarget.register_plugin_field(SkipTyField),
        PythonSourceTarget.register_plugin_field(SkipTyField),
        PythonTestsGeneratorTarget.register_plugin_field(SkipTyField),
        PythonTestTarget.register_plugin_field(SkipTyField),
        PythonTestUtilsGeneratorTarget.register_plugin_field(SkipTyField),
    )
