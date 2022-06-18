# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
from typing import Iterable

from experimental.swift.target_types import (
    SwiftFieldSet,
)
from pants.core.goals.check import CheckRequest, CheckResults
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


class SwiftCheckRequest(CheckRequest):
    field_set_type = SwiftFieldSet
    name = "swiftcp"


@rule(desc="Check Swift compilation", level=LogLevel.DEBUG)
async def swiftc_check(request: SwiftCheckRequest) -> CheckResults:
    logger.warning(request)
    return CheckResults([], checker_name=request.name)


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        UnionRule(CheckRequest, SwiftCheckRequest),
    )
