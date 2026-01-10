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


class SkipPyreflyField(BoolField):
    alias = "skip_pyrefly"
    default = False
    help = "If true, don't run Pyrefly on this target's code."


def rules() -> Iterable[Rule | UnionRule]:
    return (
        PythonSourcesGeneratorTarget.register_plugin_field(SkipPyreflyField),
        PythonSourceTarget.register_plugin_field(SkipPyreflyField),
        PythonTestsGeneratorTarget.register_plugin_field(SkipPyreflyField),
        PythonTestTarget.register_plugin_field(SkipPyreflyField),
        PythonTestUtilsGeneratorTarget.register_plugin_field(SkipPyreflyField),
    )
