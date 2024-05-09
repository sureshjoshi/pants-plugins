# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations
from typing import Iterable

from pants.engine.goal import Goal, GoalSubsystem
from pants.engine.rules import Rule, collect_rules


class MigrateSubsystem(GoalSubsystem):
    name = "migrate"
    help = "???"


class Migrate(Goal):
    subsystem_cls = MigrateSubsystem
    environment_behavior = Goal.EnvironmentBehavior.LOCAL_ONLY

def rules() -> Iterable[Rule]:
    return (
        *collect_rules(),
        *MigrateSubsystem.rules(),  # type: ignore[call-arg]
    )
