import logging
from dataclasses import dataclass

from experimental.ansible.deploy import DeploymentFieldSet, DeployResult, DeployResults
from experimental.ansible.subsystem import Ansible, AnsibleLint
from experimental.ansible.target_types import (
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlayContext,
)
from pants.backend.python.target_types import ConsoleScript
from pants.backend.python.util_rules.pex import (
    Pex,
    PexProcess,
    PexRequest,
    VenvPex,
    VenvPexProcess,
    VenvPexRequest,
)
from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.core.goals.lint import LintResult, LintResults, LintTargetsRequest
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.fs import Digest, MergeDigests, RemovePrefix
from pants.engine.process import FallibleProcessResult, ProcessCacheScope
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import (
    Address,
    FieldSet,
    HydratedSources,
    HydrateSourcesRequest,
    SingleSourceField,
    WrappedTarget,
)
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnsibleFieldSet(DeploymentFieldSet):
    required_fields = (
        AnsibleDependenciesField,
        AnsiblePlaybook,
    )

    dependencies: AnsibleDependenciesField
    playbook: AnsiblePlaybook


class AnsibleCheckRequest(CheckRequest):
    field_set_type = AnsibleFieldSet


@rule(level=LogLevel.DEBUG)
async def run_ansible_check(
    request: AnsibleCheckRequest, ansible: Ansible
) -> CheckResults:
    # if ansible.skip:
    # return CheckResults([], checker_name="Ansible")

    # TODO: Pull this out into separate rule to hydrate the playbook
    field_set: AnsibleFieldSet = request.field_sets[0]
    logger.info(field_set)
    wrapped_target = await Get(WrappedTarget, Address, field_set.address)
    target = wrapped_target.target
    sources = await Get(
        HydratedSources,
        HydrateSourcesRequest(
            target.get(SingleSourceField),
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    # Drop the top-level directory
    flattened_digest = await Get(
        Digest, RemovePrefix(sources.snapshot.digest, sources.snapshot.dirs[0])
    )

    # Install ansible
    ansible_pex = await Get(
        Pex,
        PexRequest(
            output_filename="ansible.pex",
            internal_only=True,
            requirements=ansible.pex_requirements(),
            interpreter_constraints=ansible.interpreter_constraints,
            main=ansible.main,
        ),
    )

    # Run the ansible syntax check on the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[
                "--syntax-check",
                field_set.playbook.value or field_set.playbook.default,
            ],
            description="Running Ansible syntax check...",
            input_digest=flattened_digest,
            level=LogLevel.DEBUG,
        ),
    )

    return CheckResults(
        [CheckResult.from_fallible_process_result(process_result)],
        checker_name="Ansible",
    )


@rule(level=LogLevel.DEBUG)
async def run_ansible_playbook(
    field_set: AnsibleFieldSet, ansible: Ansible
) -> DeployResults:
    # TODO: Pull this out into separate rule to hydrate the playbook
    wrapped_target = await Get(WrappedTarget, Address, field_set.address)
    target = wrapped_target.target
    sources = await Get(
        HydratedSources,
        HydrateSourcesRequest(
            target.get(SingleSourceField),
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    # Drop the top-level directory
    flattened_digest = await Get(
        Digest, RemovePrefix(sources.snapshot.digest, sources.snapshot.dirs[0])
    )

    # Install Ansible
    ansible_pex = await Get(
        Pex,
        PexRequest(
            output_filename="ansible.pex",
            internal_only=True,
            requirements=ansible.pex_requirements(),
            interpreter_constraints=ansible.interpreter_constraints,
            main=ansible.main,
        ),
    )

    # Run the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[field_set.playbook.value or field_set.playbook.default],
            description="Running Ansible Playbook...",
            input_digest=flattened_digest,
            level=LogLevel.DEBUG,
            cache_scope=ProcessCacheScope.PER_RESTART_SUCCESSFUL,
        ),
    )

    return DeployResults(
        [DeployResult.from_fallible_process_result(process_result)],
        deployer_name="Ansible",
    )


@dataclass(frozen=True)
class AnsibleLintFieldSet(FieldSet):
    required_fields = (
        AnsiblePlaybook,
        AnsiblePlayContext,
    )

    playbook: AnsiblePlaybook
    ansiblecontext: AnsiblePlayContext


class AnsibleLintRequest(LintTargetsRequest):
    field_set_type = AnsibleLintFieldSet
    name = "ansible-lint"


@rule
async def run_ansiblelint(
    request: AnsibleLintRequest, ansible_lint: AnsibleLint
) -> LintResults:

    logger.info([request.field_sets[0].playbook])  # + request.field_sets[0].
    logger.info("HIHELLO")

    source_files_get = Get(
        SourceFiles,
        SourceFilesRequest(
            field_set.ansiblecontext for field_set in request.field_sets
        ),
    )
    source_files = await source_files_get
    source_files_snapshot = source_files.snapshot
    input_digest = await Get(Digest, MergeDigests((source_files_snapshot.digest,)))

    # # TODO: Pull this out into separate rule to hydrate the playbook
    # field_set: AnsibleFieldSet = request.field_sets[0]
    # logger.info(field_set)
    # wrapped_target = await Get(WrappedTarget, Address, field_set.address)
    # target = wrapped_target.target
    # sources = await Get(
    #     HydratedSources,
    #     HydrateSourcesRequest(
    #         target.get(SingleSourceField),
    #         for_sources_types=(AnsiblePlaybook,),
    #     ),
    # )

    # # Drop the top-level directory
    # flattened_digest = await Get(Digest, RemovePrefix(sources.snapshot.digest, sources.snapshot.dirs[0]))

    # Install ansible
    ansible_pex = await Get(
        Pex,
        PexRequest(
            output_filename="ansible-lint.pex",
            internal_only=True,
            requirements=ansible_lint.pex_requirements(),
            interpreter_constraints=ansible_lint.interpreter_constraints,
            main=ansible_lint.main,
            additional_args=("--venv", "prepend"),
        ),
    )

    # Run the ansible syntax check on the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[],
            description="Running Ansible syntax check...",
            input_digest=input_digest,
            level=LogLevel.DEBUG,
        ),
    )

    return LintResults(
        [LintResult.from_fallible_process_result(process_result)],
        linter_name="ansible-lint",
    )


def rules():
    return (
        *collect_rules(),
        UnionRule(CheckRequest, AnsibleCheckRequest),
        UnionRule(LintTargetsRequest, AnsibleLintRequest),
        UnionRule(DeploymentFieldSet, AnsibleFieldSet),
    )
