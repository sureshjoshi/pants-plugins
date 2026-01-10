# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

"""A fast type checker and language server for Python.

See https://github.com/facebook/pyrefly for details.
"""

from __future__ import annotations

from collections.abc import Iterable

from experimental.pyrefly.rules import rules as pyrefly_rules
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (*pyrefly_rules(),)
