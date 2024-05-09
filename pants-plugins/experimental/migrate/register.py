# Copyright 2024 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable

from experimental.migrate.rules import rules as migrate_rules
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (*migrate_rules(),)
