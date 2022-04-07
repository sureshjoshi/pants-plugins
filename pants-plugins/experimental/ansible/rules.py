from __future__ import annotations

import logging
from dataclasses import dataclass

from experimental.ansible.deploy import DeploymentFieldSet, DeployResult, DeployResults
from experimental.ansible.sources import (
    AnsibleFieldSet,
    AnsibleSources,
    AnsibleSourcesCollection,
    AnsibleSourcesDigest,
)
from experimental.ansible.subsystems.ansible import Ansible
from experimental.ansible.subsystems.ansible_galaxy import AnsibleGalaxy
from experimental.ansible.subsystems.ansible_lint import AnsibleLint
from experimental.ansible.target_types import AnsiblePlaybook
from pants.backend.python.util_rules.pex import Pex, PexProcess, PexRequest
from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.core.goals.lint import LintResult, LintResults, LintTargetsRequest
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.fs import Digest, MergeDigests
from pants.engine.internals.native_engine import EMPTY_DIGEST
from pants.engine.process import FallibleProcessResult, ProcessCacheScope
from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import FieldSet, HydratedSources, HydrateSourcesRequest
from pants.engine.unions import UnionRule
from pants.option.option_types import StrListOption, StrOption
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


@rule
async def resolve_ansible_context(
    contexts: AnsibleSourcesCollection,
) -> AnsibleSourcesDigest:
    """Resolve Ansible play contexts into their Digests, ready for use as files"""
    source_files_get = Get(
        SourceFiles,
        SourceFilesRequest(contexts),
    )
    source_files = await source_files_get
    input_digest = Get(Digest, MergeDigests((source_files.snapshot.digest,)))

    return AnsibleSourcesDigest(await input_digest)


@dataclass(frozen=True, unsafe_hash=True)
class AnsibleGalaxyDependencyRequest:
    requirements: StrOption
    collections: StrListOption
    collections_path: StrOption
    existing_files: Digest  # TODO: Extract the requirements file only
    pex: Pex


@dataclass(frozen=True)
class AnsibleGalaxyDependencies:
    galaxy_requirements: Digest = EMPTY_DIGEST
    galaxy_collections: Digest = EMPTY_DIGEST


@rule
async def resolve_ansible_galaxy_dependencies(
    galaxy_request: AnsibleGalaxyDependencyRequest,
) -> AnsibleGalaxyDependencies:
    galaxy_requirements_digest = EMPTY_DIGEST
    if galaxy_request.requirements:
        # Install any top-level Galaxy requirements
        galaxy_requirements_process_result = await Get(
            FallibleProcessResult,
            PexProcess(
                galaxy_request.pex,
                argv=(
                    "collection",
                    "install",
                    "-r",
                    galaxy_request.requirements,
                    "-p",
                    galaxy_request.collections_path,
                ),
                description=f"Installing ansible-galaxy from {galaxy_request.requirements}",
                input_digest=galaxy_request.existing_files.digest,
                output_directories=(galaxy_request.collections_path,),
                level=LogLevel.DEBUG,
                cache_scope=ProcessCacheScope.PER_RESTART_SUCCESSFUL,
            ),
        )
        galaxy_requirements_digest = galaxy_requirements_process_result.output_digest

    galaxy_collections_digest = EMPTY_DIGEST
    if galaxy_request.collections:
        # Install any top-level Galaxy collections
        galaxy_process_result = await Get(
            FallibleProcessResult,
            PexProcess(
                galaxy_request.pex,
                argv=(
                    "collection",
                    "install",
                    *galaxy_request.collections,
                    "-p",
                    galaxy_request.collections_path,
                ),
                description="Installing ansible-galaxy collections",
                output_directories=(galaxy_request.collections_path,),
                level=LogLevel.DEBUG,
                cache_scope=ProcessCacheScope.PER_RESTART_SUCCESSFUL,
            ),
        )
        galaxy_collections_digest = galaxy_process_result.output_digest

    return AnsibleGalaxyDependencies(
        galaxy_requirements_digest, galaxy_collections_digest
    )


class AnsibleCheckRequest(CheckRequest):
    field_set_type = AnsibleFieldSet
    name = Ansible.options_scope


@rule(level=LogLevel.DEBUG)
async def run_ansible_check(
    request: AnsibleCheckRequest, ansible: Ansible, galaxy: AnsibleGalaxy
) -> CheckResults:

    context_files_get = Get(
        AnsibleSourcesDigest,
        AnsibleSourcesCollection,
        AnsibleSourcesCollection.from_request(request),
    )

    playbook_get = Get(
        HydratedSources,
        HydrateSourcesRequest(
            request.field_sets[0].playbook,
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    ansible_pex_get = Get(Pex, PexRequest, ansible.to_pex_request())
    galaxy_pex_get = Get(Pex, PexRequest, galaxy.to_pex_request())

    context_files, playbook, ansible_pex, galaxy_pex = await MultiGet(
        context_files_get, playbook_get, ansible_pex_get, galaxy_pex_get
    )

    galaxy_dependencies = await Get(
        AnsibleGalaxyDependencies,
        AnsibleGalaxyDependencyRequest(
            galaxy.requirements,
            galaxy.collections,
            galaxy.collections_path,
            context_files,
            galaxy_pex,
        ),
    )

    # Combine Galaxy dependencies and Playbook context
    merged_digest = await Get(
        Digest,
        MergeDigests(
            [
                context_files.digest,
                galaxy_dependencies.galaxy_requirements,
                galaxy_dependencies.galaxy_collections,
            ]
        ),
    )

    # Run the ansible syntax check on the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[
                "--syntax-check",
                playbook.snapshot.files[0],
            ],
            description="Running Ansible syntax check...",
            input_digest=merged_digest,
            level=LogLevel.DEBUG,
            extra_env={"ANSIBLE_COLLECTIONS_PATHS": galaxy.collections_path},
        ),
    )

    return CheckResults(
        [CheckResult.from_fallible_process_result(process_result)],
        checker_name="Ansible",
    )


@rule(level=LogLevel.DEBUG)
async def run_ansible_playbook(
    request: AnsibleFieldSet, ansible: Ansible, galaxy: AnsibleGalaxy
) -> DeployResults:
    context_files_get = Get(
        AnsibleSourcesDigest,
        AnsibleSourcesCollection([request.sources]),
    )

    playbook_get = Get(
        HydratedSources,
        HydrateSourcesRequest(
            request.playbook,
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    # Install Ansible
    ansible_pex_get = Get(Pex, PexRequest, ansible.to_pex_request())
    galaxy_pex_get = Get(Pex, PexRequest, galaxy.to_pex_request())

    context_files, playbook, ansible_pex, galaxy_pex = await MultiGet(
        context_files_get, playbook_get, ansible_pex_get, galaxy_pex_get
    )

    galaxy_dependencies = await Get(
        AnsibleGalaxyDependencies,
        AnsibleGalaxyDependencyRequest(
            galaxy.requirements,
            galaxy.collections,
            galaxy.collections_path,
            context_files,
            galaxy_pex,
        ),
    )

    # Combine Galaxy dependencies and Playbook context
    merged_digest = await Get(
        Digest,
        MergeDigests(
            [
                context_files.digest,
                galaxy_dependencies.galaxy_requirements,
                galaxy_dependencies.galaxy_collections,
            ]
        ),
    )

    playbook_filename = playbook.snapshot.files[0]
    argv = [playbook_filename, *ansible.args]
    argv.extend(request.ansible_playbook_args.value)
    # Run the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=argv,
            description="Running Ansible Playbook...",
            input_digest=merged_digest,
            level=LogLevel.DEBUG,
            cache_scope=ProcessCacheScope.PER_RESTART_SUCCESSFUL,
            extra_env={"ANSIBLE_COLLECTIONS_PATHS": galaxy.collections_path},
        ),
    )

    return DeployResults(
        [DeployResult.from_fallible_process_result(process_result)],
        deployer_name=Ansible.options_scope,
    )


@dataclass(frozen=True)
class AnsibleLintFieldSet(FieldSet):
    required_fields = (AnsibleSources,)

    sources: AnsibleSources


class AnsibleLintRequest(LintTargetsRequest):
    field_set_type = AnsibleLintFieldSet
    name = "ansible-lint"


@rule
async def run_ansiblelint(
    request: AnsibleLintRequest, ansible_lint: AnsibleLint
) -> LintResults:

    contexts = AnsibleSourcesCollection.from_request(request)
    input_digest, ansible_pex = await MultiGet(
        Get(
            AnsibleSourcesDigest,
            AnsibleSourcesCollection,
            contexts,
        ),
        Get(
            Pex,
            PexRequest(
                output_filename="ansible-lint.pex",
                internal_only=True,
                requirements=ansible_lint.pex_requirements(),
                interpreter_constraints=ansible_lint.interpreter_constraints,
                main=ansible_lint.main,
                additional_args=("--venv", "prepend"),
            ),
        ),
    )

    args = ["-f", "pep8"]
    args.extend(ansible_lint.args)

    # Run the ansible syntax check on the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=args,
            description="Running Ansible syntax check...",
            input_digest=input_digest.digest,
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
