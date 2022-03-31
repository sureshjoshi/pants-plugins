from __future__ import annotations

import logging
from abc import ABCMeta
from dataclasses import dataclass
from typing import Any, Iterable

from pants.engine.console import Console
from pants.engine.engine_aware import EngineAwareReturnType
from pants.engine.fs import EMPTY_DIGEST, Digest
from pants.engine.goal import Goal, GoalSubsystem
from pants.engine.process import FallibleProcessResult
from pants.engine.rules import Get, collect_rules, goal_rule
from pants.engine.target import (
    FieldSet,
    NoApplicableTargetsBehavior,
    TargetRootsToFieldSets,
    TargetRootsToFieldSetsRequest,
)
from pants.engine.unions import union
from pants.util.logging import LogLevel
from pants.util.memo import memoized_property
from pants.util.meta import frozen_after_init
from pants.util.strutil import strip_v2_chroot_path

logger = logging.getLogger(__name__)

# TODO: Copied from LintResult/CheckResult - can this be inherited or composed?
@dataclass(frozen=True)
class DeployResult:
    exit_code: int
    stdout: str
    stderr: str
    partition_description: str | None = None
    report: Digest = EMPTY_DIGEST

    @classmethod
    def from_fallible_process_result(
        cls,
        process_result: FallibleProcessResult,
        *,
        partition_description: str | None = None,
        strip_chroot_path: bool = False,
        report: Digest = EMPTY_DIGEST,
    ) -> DeployResult:
        def prep_output(s: bytes) -> str:
            return strip_v2_chroot_path(s) if strip_chroot_path else s.decode()

        return cls(
            exit_code=process_result.exit_code,
            stdout=prep_output(process_result.stdout),
            stderr=prep_output(process_result.stderr),
            partition_description=partition_description,
            report=report,
        )

    def metadata(self) -> dict[str, Any]:
        return {"partition": self.partition_description}


# TODO: Copied from LintResult/CheckResult - can this be inherited or composed?
@frozen_after_init
@dataclass(unsafe_hash=True)
class DeployResults(EngineAwareReturnType):
    results: tuple[DeployResult, ...]
    deployer_name: str

    def __init__(self, results: Iterable[DeployResult], *, deployer_name: str) -> None:
        self.results = tuple(results)
        self.deployer_name = deployer_name

    @property
    def skipped(self) -> bool:
        return bool(self.results) is False

    @memoized_property
    def exit_code(self) -> int:
        return next(
            (result.exit_code for result in self.results if result.exit_code != 0), 0
        )

    def level(self) -> LogLevel | None:
        if self.skipped:
            return LogLevel.DEBUG
        return LogLevel.ERROR if self.exit_code != 0 else LogLevel.INFO

    def message(self) -> str | None:
        if self.skipped:
            return f"{self.deployer_name} skipped."
        message = self.deployer_name
        message += (
            " succeeded."
            if self.exit_code == 0
            else f" failed (exit code {self.exit_code})."
        )

        def msg_for_result(result: DeployResult) -> str:
            msg = ""
            if result.stdout:
                msg += f"\n{result.stdout}"
            if result.stderr:
                msg += f"\n{result.stderr}"
            if msg:
                msg = f"{msg.rstrip()}\n\n"
            return msg

        if len(self.results) == 1:
            results_msg = msg_for_result(self.results[0])
        else:
            results_msg = "\n"
            for i, result in enumerate(self.results):
                msg = f"Partition #{i + 1}"
                msg += (
                    f" - {result.partition_description}:"
                    if result.partition_description
                    else ":"
                )
                msg += msg_for_result(result) or "\n\n"
                results_msg += msg
        message += results_msg
        return message

    def cacheable(self) -> bool:
        """Is marked uncacheable to ensure that it always renders."""
        return False


@union
class DeploymentFieldSet(FieldSet, metaclass=ABCMeta):
    """The fields necessary to deploy an asset."""


class DeploySubsystem(GoalSubsystem):
    name = "deploy"
    help = "Deploy packages to a remote."

    required_union_implementations = (DeploymentFieldSet,)


class Deploy(Goal):
    subsystem_cls = DeploySubsystem


@goal_rule
async def deploy(
    console: Console,
    deploy: DeploySubsystem,
) -> Deploy:
    target_roots_to_deployment_field_sets = await Get(
        TargetRootsToFieldSets,
        TargetRootsToFieldSetsRequest(
            DeploymentFieldSet,
            goal_description="",
            no_applicable_targets_behavior=NoApplicableTargetsBehavior.error,
            expect_single_field_set=True,
        ),
    )

    field_set = target_roots_to_deployment_field_sets.field_sets[0]
    request = await Get(DeployResults, DeploymentFieldSet, field_set)
    # TODO: Do something with the result
    return Deploy(exit_code=0)


def rules():
    return collect_rules()
