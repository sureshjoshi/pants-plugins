# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

"""An extremely fast Python type checker and language server, written in Rust.

See https://github.com/astral-sh/ty for details.
"""

from __future__ import annotations

from collections.abc import Iterable

from experimental.ty.rules import rules as ty_rules
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (*ty_rules(),)
