from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Protocol

from experimental.ansible.deploy import DeploymentFieldSet, DeployResult, DeployResults
from experimental.ansible.subsystem import Ansible, AnsibleLint
from experimental.ansible.target_types import (
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlayContext,
)
from pants.backend.python.util_rules.pex import Pex, PexProcess, PexRequest
from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.core.goals.lint import LintResult, LintResults, LintTargetsRequest
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.collection import Collection
from pants.engine.fs import Digest, MergeDigests
from pants.engine.process import FallibleProcessResult, ProcessCacheScope
from pants.engine.rules import Get, MultiGet, collect_rules, rule
from pants.engine.target import FieldSet, HydratedSources, HydrateSourcesRequest
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnsibleSourcesDigest:
    digest: Digest


@dataclass(frozen=True)
class AnsibleFieldSet(DeploymentFieldSet):
    required_fields = (
        AnsibleDependenciesField,
        AnsiblePlaybook,
        AnsiblePlayContext,
    )

    dependencies: AnsibleDependenciesField
    playbook: AnsiblePlaybook
    ansiblecontext: AnsiblePlayContext


class AnsibleCheckRequest(CheckRequest):
    field_set_type = AnsibleFieldSet
    name = "ansible syntax check"


class HasContext(Protocol):
    ansiblecontext: AnsiblePlayContext


class RequestHasContext(Protocol):
    field_sets: Iterable[HasContext]


class AnsibleContexts(Collection[AnsiblePlayContext]):
    ...

    @classmethod
    def from_request(cls, request: RequestHasContext) -> AnsibleContexts:
        return AnsibleContexts(
            [field_set.ansiblecontext for field_set in request.field_sets]
        )


@rule
async def resolve_ansible_context(
    contexts: AnsibleContexts,
) -> AnsibleSourcesDigest:
    """Resolve Ansible play contexts into their Digests, ready for use as files"""
    source_files_get = Get(
        SourceFiles,
        SourceFilesRequest(contexts),
    )
    source_files = await source_files_get
    input_digest = Get(Digest, MergeDigests((source_files.snapshot.digest,)))

    return AnsibleSourcesDigest(await input_digest)


@rule(level=LogLevel.DEBUG)
async def run_ansible_check(
    request: AnsibleCheckRequest, ansible: Ansible
) -> CheckResults:

    context_files_get = Get(
        AnsibleSourcesDigest, AnsibleContexts, AnsibleContexts.from_request(request)
    )

    playbook_get = Get(
        HydratedSources,
        HydrateSourcesRequest(
            request.field_sets[0].playbook,
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    # Install ansible
    ansible_pex_get = Get(
        Pex,
        PexRequest(
            output_filename="ansible.pex",
            internal_only=True,
            requirements=ansible.pex_requirements(),
            interpreter_constraints=ansible.interpreter_constraints,
            main=ansible.main,
        ),
    )

    context_files, playbook, ansible_pex = await MultiGet(
        context_files_get, playbook_get, ansible_pex_get
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
            input_digest=context_files.digest,
            level=LogLevel.DEBUG,
        ),
    )

    return CheckResults(
        [CheckResult.from_fallible_process_result(process_result)],
        checker_name="Ansible",
    )


@rule(level=LogLevel.DEBUG)
async def run_ansible_playbook(
    request: AnsibleFieldSet, ansible: Ansible
) -> DeployResults:
    context_files_get = Get(
        AnsibleSourcesDigest,
        AnsibleContexts([request.ansiblecontext]),
    )

    playbook_get = Get(
        HydratedSources,
        HydrateSourcesRequest(
            request.playbook,
            for_sources_types=(AnsiblePlaybook,),
        ),
    )

    # Install Ansible
    ansible_pex_get = Get(
        Pex,
        PexRequest(
            output_filename="ansible.pex",
            internal_only=True,
            requirements=ansible.pex_requirements(),
            interpreter_constraints=ansible.interpreter_constraints,
            main=ansible.main,
        ),
    )

    context_files, playbook, ansible_pex = await MultiGet(
        context_files_get, playbook_get, ansible_pex_get
    )

    # Run the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[playbook.snapshot.files[0]],
            description="Running Ansible Playbook...",
            input_digest=context_files.digest,
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

    contexts = AnsibleContexts.from_request(request)
    input_digest, ansible_pex = await MultiGet(
        Get(
            AnsibleSourcesDigest,
            AnsibleContexts,
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

    # Run the ansible syntax check on the passed-in playbook
    process_result = await Get(
        FallibleProcessResult,
        PexProcess(
            ansible_pex,
            argv=[],
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
