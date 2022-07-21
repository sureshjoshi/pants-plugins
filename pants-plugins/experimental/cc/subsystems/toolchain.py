from __future__ import annotations

from typing import Iterable
from pants.engine.rules import collect_rules, Rule, UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return collect_rules()
