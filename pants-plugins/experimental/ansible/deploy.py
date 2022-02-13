from abc import ABCMeta

from pants.engine.console import Console
from pants.engine.goal import Goal, GoalSubsystem
from pants.engine.rules import collect_rules, goal_rule
from pants.engine.target import FieldSet, Targets
from pants.engine.unions import union


@union
class DeploymentFieldSet(FieldSet, metaclass=ABCMeta):
    """The fields necessary to deploy an asset."""


class DeploySubsystem(GoalSubsystem):
    name = "deploy"
    help = "Deploy packages to a remote."


class Deploy(Goal):
    subsystem_cls = DeploySubsystem


@goal_rule
async def deploy(
    console: Console,
    targets: Targets,
) -> Deploy:
    return Deploy(exit_code=0)


def rules():
    return collect_rules()
