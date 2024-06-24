from __future__ import annotations

from collections.abc import Iterable

from experimental.plugin.rules import rules as plugin_rules
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (*plugin_rules(),)
