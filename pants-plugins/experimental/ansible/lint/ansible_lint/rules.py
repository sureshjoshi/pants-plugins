# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from experimental.ansible.lint.ansible_lint.subsystem import AnsibleLint
from experimental.ansible.target_types import AnsibleSourceField
from pants.backend.python.util_rules.pex import PexRequest, VenvPex, VenvPexProcess
from pants.core.goals.lint import LintResult, LintResults, LintTargetsRequest
from pants.core.util_rules.config_files import ConfigFiles, ConfigFilesRequest
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.fs import Digest, MergeDigests
from pants.engine.process import FallibleProcessResult
from pants.engine.rules import Get, MultiGet, Rule, collect_rules, rule
from pants.engine.target import FieldSet
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnsibleLintFieldSet(FieldSet):
    required_fields = (AnsibleSourceField,)

    source: AnsibleSourceField


class AnsibleLintRequest(LintTargetsRequest):
    field_set_type = AnsibleLintFieldSet
    name = AnsibleLint.options_scope


@dataclass(frozen=True)
class SetupRequest:
    request: AnsibleLintRequest
    check_only: bool


@dataclass(frozen=True)
class Setup:
    process: VenvPexProcess
    original_digest: Digest


@rule(level=LogLevel.DEBUG)
async def setup_ansible_lint(
    setup_request: SetupRequest, ansible_lint: AnsibleLint
) -> Setup:
    source_files_get = Get(
        SourceFiles,
        SourceFilesRequest(
            field_set.source for field_set in setup_request.request.field_sets
        ),
    )

    ansiblelint_pex, source_files = await MultiGet(
        Get(VenvPex, PexRequest, ansible_lint.to_pex_request()),
        source_files_get,
    )

    # Look for any/all of the ansible_lint configuration files (recurse sub-dirs)
    config_files = await Get(
        ConfigFiles,
        ConfigFilesRequest,
        ansible_lint.config_request(source_files.snapshot.dirs),
    )

    # Merge source files, config files, and ansible_lint pex process
    input_digest = await Get(
        Digest,
        MergeDigests(
            [
                source_files.snapshot.digest,
                config_files.snapshot.digest,
                ansiblelint_pex.digest,
            ]
        ),
    )

    process = VenvPexProcess(
        ansiblelint_pex,
        argv=(
            "--parseable",  # Output formatting (same as "-f pep8")
            # "--write" if not setup_request.check_only else "",
            *ansible_lint.args,  # User-added arguments
        ),
        input_digest=input_digest,
        output_files=source_files.snapshot.files,
        description=f"Run ansible-lint on {pluralize(len(source_files.snapshot.files), 'file')}.",
        level=LogLevel.DEBUG,
    )
    return Setup(process, original_digest=source_files.snapshot.digest)


# @rule(level=LogLevel.DEBUG)
# async def ansible_lint_fmt(
#     request: AnsibleLintRequest, ansible_lint: AnsibleLint
# ) -> FmtResult:
#     """ansible-lint is not a dedicated formatter, but rather it's a best-effort one.
#     This means that using format results as lint results will not work"""
#     if ansible_lint.skip:
#         return FmtResult.skip(formatter_name=request.name)

#     setup = await Get(Setup, SetupRequest(request, check_only=False))
#     result = await Get(FallibleProcessResult, VenvPexProcess, setup.process)
#     output_snapshot = await Get(Snapshot, Digest, result.output_digest)
#     return FmtResult.create(request, result, output_snapshot, strip_chroot_path=True)


@rule(level=LogLevel.DEBUG)
async def ansible_lint(
    request: AnsibleLintRequest, ansible_lint: AnsibleLint
) -> LintResults:
    if ansible_lint.skip:
        return LintResults([], linter_name=request.name)

    setup = await Get(Setup, SetupRequest(request, check_only=True))
    result = await Get(FallibleProcessResult, VenvPexProcess, setup.process)
    return LintResults(
        [LintResult.from_fallible_process_result(result)], linter_name=request.name
    )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        # UnionRule(FmtRequest, AnsibleLintRequest),
        UnionRule(LintTargetsRequest, AnsibleLintRequest),
    )
