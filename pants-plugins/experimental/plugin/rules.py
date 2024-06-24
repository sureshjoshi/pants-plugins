from __future__ import annotations

from collections.abc import Iterable
from enum import Enum

from pants.backend.project_info.peek import TargetDatas
from pants.engine.console import Console
from pants.engine.goal import Goal, GoalSubsystem, Outputting
from pants.engine.rules import Get, Rule, collect_rules, goal_rule
from pants.engine.target import UnexpandedTargets
from pants.option.option_types import EnumOption, StrOption

class PluginType(Enum):
    BUILTIN = "builtin"
    GOAL = "goal"
    LINTER = "linter"


class PluginSubsystem(GoalSubsystem):
    name = "plugin-init"
    help = "???"

    plugin_name = StrOption(
        "--name",
        default=None,
        help="The name of the plugin to create.",
    )

    type = EnumOption(
        default=None,
        enum_type=PluginType,
        help="The type of plugin to create.",
    )


class Plugin(Goal):
    subsystem_cls = PluginSubsystem
    environment_behavior = Goal.EnvironmentBehavior.LOCAL_ONLY


@goal_rule
async def plugin(
    console: Console,
    subsystem: PluginSubsystem,
    # targets: UnexpandedTargets,
) -> Plugin:
    if not subsystem.type:
        console.input(f"What type of plugin do you want to create? {[p.value for p in PluginType]} ")
        
    return Plugin(exit_code=0)


def rules() -> Iterable[Rule]:
    return collect_rules()
