# Copyright 2024 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePath
from typing import Final, Iterable, Mapping

from pants.engine.console import Console
from pants.engine.rules import Get, MultiGet, Rule, collect_rules, goal_rule, rule
from pants.engine.target import SourcesField, UnexpandedTargets
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

from experimental.migrate.subsystems import Migrate, MigrateSubsystem

# TODO: This will need to become a BuiltinGoal, so just hacking around to get a list of Targets
# Normally, will use the same code for "call-by-name-migration"
@goal_rule
async def migrate(console: Console, subsystem: MigrateSubsystem, targets: UnexpandedTargets) -> Migrate:
    for target in targets:
        if target.address.is_file_target:
            print(target.address.filename)

    filenames = [t.address.filename for t in targets if t.address.is_file_target]

    for f in sorted(filenames):
        file = Path(f)
        

    return Migrate(exit_code=0)


def rules() -> Iterable[Rule]:
    return collect_rules()
