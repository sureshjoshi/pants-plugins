import logging
from dataclasses import dataclass

from experimental.ansible.deploy import DeploymentFieldSet, DeployResult, DeployResults
from experimental.ansible.subsystem import Ansible
from experimental.ansible.target_types import AnsibleDependenciesField, AnsiblePlaybook
from pants.backend.python.util_rules.pex import Pex, PexProcess, PexRequest
from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.core.util_rules.source_files import SourceFilesRequest
from pants.core.util_rules.stripped_source_files import StrippedSourceFiles
from pants.engine.fs import Digest, RemovePrefix
from pants.engine.process import FallibleProcessResult, ProcessCacheScope
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import (
    Address,
    DependenciesRequest,
    HydratedSources,
    HydrateSourcesRequest,
    SingleSourceField,
    SourcesField,
    Targets,
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
    name = Ansible.options_scope


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
        checker_name=request.name,
    )


@rule(level=LogLevel.DEBUG)
async def run_ansible_playbook(
    field_set: AnsibleFieldSet, ansible: Ansible
) -> DeployResults:
    direct_deps = await Get(Targets, DependenciesRequest(field_set.dependencies))

    stripped_sources = await Get(
        StrippedSourceFiles,
        SourceFilesRequest(
            sources_fields=[tgt.get(SourcesField) for tgt in direct_deps],
        ),
    )

    # Install Ansible
    ansible_pex = await Get(
        Pex,
        PexRequest,
        ansible.to_pex_request(),
    )

    # Run the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[field_set.playbook.value or field_set.playbook.default],
            description="Running Ansible Playbook...",
            input_digest=stripped_sources.snapshot.digest,
            level=LogLevel.DEBUG,
            cache_scope=ProcessCacheScope.PER_RESTART_SUCCESSFUL,
        ),
    )

    return DeployResults(
        [DeployResult.from_fallible_process_result(process_result)],
        deployer_name=Ansible.options_scope,
    )


def rules():
    return (
        *collect_rules(),
        UnionRule(CheckRequest, AnsibleCheckRequest),
        UnionRule(DeploymentFieldSet, AnsibleFieldSet),
    )
