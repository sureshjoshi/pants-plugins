# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from experimental.ansible.lint.ansible_lint.subsystem import AnsibleLint
from experimental.ansible.target_types import AnsibleSourceField
from pants.backend.python.util_rules.pex import Pex, PexProcess, PexRequest
from pants.core.goals.fmt import FmtRequest, FmtResult
from pants.core.util_rules.config_files import ConfigFiles, ConfigFilesRequest
from pants.engine.fs import Digest, MergeDigests, Snapshot
from pants.engine.process import ProcessResult
from pants.engine.rules import Get, MultiGet, Rule, collect_rules, rule
from pants.engine.target import FieldSet
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnsibleLintFmtFieldSet(FieldSet):
    required_fields = (AnsibleSourceField,)

    sources: AnsibleSourceField


class AnsibleLintFormatRequest(FmtRequest):
    field_set_type = AnsibleLintFmtFieldSet
    name = AnsibleLint.options_scope


@rule(level=LogLevel.DEBUG)
async def ansible_lint_fmt(
    request: AnsibleLintFormatRequest, ansible_lint: AnsibleLint
) -> FmtResult:
    if ansible_lint.skip:
        return FmtResult.skip(formatter_name=request.name)

    # Look for any/all of the ansible_lint configuration files (recurse sub-dirs)
    config_files_get = Get(
        ConfigFiles,
        ConfigFilesRequest,
        ansible_lint.config_request(request.snapshot.dirs),
    )

    ansiblelint_pex, config_files = await MultiGet(
        Get(Pex, PexRequest, ansible_lint.to_pex_request()), config_files_get
    )

    # Merge source files, config files, and ansible_lint pex process
    input_digest = await Get(
        Digest,
        MergeDigests(
            [
                request.snapshot.digest,
                config_files.snapshot.digest,
                ansiblelint_pex.digest,
            ]
        ),
    )

    result = await Get(
        ProcessResult,
        PexProcess(
            ansiblelint_pex,
            argv=(
                *ansible_lint.args,  # User-added arguments
                # *request.snapshot.files,
            ),
            input_digest=input_digest,
            output_files=request.snapshot.files,
            description=f"Run ansible-lint on {pluralize(len(request.snapshot.files), 'file')}.",
            level=LogLevel.DEBUG,
        ),
    )
    output_snapshot = await Get(Snapshot, Digest, result.output_digest)
    return FmtResult.create(request, result, output_snapshot, strip_chroot_path=True)


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        UnionRule(FmtRequest, AnsibleLintFormatRequest),
    )
