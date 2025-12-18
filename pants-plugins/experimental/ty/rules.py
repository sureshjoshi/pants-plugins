# Copyright 2025 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass

from experimental.ty.skip_field import SkipTyField
from experimental.ty.subsystems import Ty
from pants.backend.python.subsystems.setup import PythonSetup
from pants.backend.python.target_types import (
    InterpreterConstraintsField,
    PythonResolveField,
    PythonSourceField,
)
from pants.backend.python.util_rules import pex_from_targets
from pants.backend.python.util_rules.interpreter_constraints import (
    InterpreterConstraints,
)
from pants.backend.python.util_rules.partition import (
    _partition_by_interpreter_constraints_and_resolve,
)
from pants.backend.python.util_rules.pex import (
    PexRequest,
    VenvPexProcess,
    VenvPexRequest,
    create_pex,
    create_venv_pex,
)
from pants.backend.python.util_rules.pex_environment import PexEnvironment
from pants.backend.python.util_rules.pex_from_targets import RequirementsPexRequest
from pants.backend.python.util_rules.python_sources import (
    PythonSourceFilesRequest,
    prepare_python_sources,
)
from pants.core.goals.check import CheckRequest, CheckResult, CheckResults
from pants.core.util_rules import config_files
from pants.core.util_rules.config_files import find_config_file
from pants.core.util_rules.external_tool import download_external_tool
from pants.core.util_rules.source_files import (
    SourceFilesRequest,
    determine_source_files,
)
from pants.engine.collection import Collection
from pants.engine.fs import MergeDigests
from pants.engine.internals.graph import resolve_coarsened_targets
from pants.engine.intrinsics import execute_process, merge_digests
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope, execute_process_or_raise
from pants.engine.rules import Rule, collect_rules, concurrently, implicitly, rule
from pants.engine.target import (
    CoarsenedTargets,
    CoarsenedTargetsRequest,
    FieldSet,
    Target,
)
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.util.ordered_set import FrozenOrderedSet, OrderedSet
from pants.util.strutil import pluralize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TyFieldSet(FieldSet):
    required_fields = (PythonSourceField,)
    sources: PythonSourceField
    resolve: PythonResolveField
    interpreter_constraints: InterpreterConstraintsField

    @classmethod
    def opt_out(cls, tgt: Target) -> bool:
        return tgt.get(SkipTyField).value


class TyRequest(CheckRequest):
    field_set_type = TyFieldSet
    tool_name = Ty.options_scope


@dataclass(frozen=True)
class TyPartition:
    field_sets: FrozenOrderedSet[TyFieldSet]
    root_targets: CoarsenedTargets
    resolve_description: str | None
    interpreter_constraints: InterpreterConstraints

    def description(self) -> str:
        ics = str(sorted(str(c) for c in self.interpreter_constraints))
        return f"{self.resolve_description}, {ics}" if self.resolve_description else ics


class TyPartitions(Collection[TyPartition]):
    pass


@rule(
    desc="Ty typecheck each partition based on its interpreter_constraints",
    level=LogLevel.DEBUG,
)
async def ty_typecheck_partition(
    partition: TyPartition,
    ty: Ty,
    platform: Platform,
    pex_environment: PexEnvironment,
) -> CheckResult:
    ty_tool, config_files, roots_sources, transitive_sources, requirements_pex = await concurrently(
        download_external_tool(ty.get_request(platform)),
        find_config_file(ty.config_request()),
        determine_source_files(SourceFilesRequest(fs.sources for fs in partition.field_sets)),
        prepare_python_sources(
            PythonSourceFilesRequest(partition.root_targets.closure()), **implicitly()
        ),
        create_pex(
            **implicitly(
                RequirementsPexRequest(
                    (fs.address for fs in partition.field_sets),
                    hardcoded_interpreter_constraints=partition.interpreter_constraints,
                )
            )
        ),
    )

    # Create a venv with the 3rd-party requirements and let Ty know about it using `--venv`
    complete_pex_env = pex_environment.in_workspace()
    requirements_venv_pex = await create_venv_pex(
        VenvPexRequest(
            PexRequest(
                output_filename="requirements_venv.pex",
                internal_only=True,
                pex_path=[requirements_pex],
                interpreter_constraints=partition.interpreter_constraints,
            ),
            complete_pex_env,
        ),
        **implicitly(),
    )

    # Force the requirements venv to materialize always by running a no-op.
    # This operation must be called with `ProcessCacheScope.SESSION`
    # so that it runs every time.
    # TODO: Cargo culted from the Pyright backend
    _ = await execute_process_or_raise(
        **implicitly(
            VenvPexProcess(
                requirements_venv_pex,
                description="Force venv to materialize",
                argv=["-c", "''"],
                cache_scope=ProcessCacheScope.PER_SESSION,
            )
        )
    )

    input_digest = await merge_digests(
        MergeDigests(
            (
                # roots_sources.snapshot.digest,
                transitive_sources.source_files.snapshot.digest,
                config_files.snapshot.digest,
                requirements_venv_pex.digest,
            )
        )
    )

    immutable_input_key = "__ty_tool"
    exe_path = os.path.join(immutable_input_key, ty_tool.exe)

    # TODO: If finding the minimum failed, just arbitrarily hardcoded it to 3.10...
    python_version = (
        partition.interpreter_constraints.minimum_python_version(
            ["3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
        )
        or "3.10"
    )
    # TODO: Handle this properly, checking out the various ways we can set the correct python version from config, pants, universe, etc
    initial_args = (
        "check",
        f"--python-version={python_version}",
        # TODO: This is greasy...
        f"--venv={os.path.join(complete_pex_env.pex_root, requirements_venv_pex.venv_rel_dir)}",
    )
    result = await execute_process(
        Process(
            argv=(exe_path, *initial_args, *ty.args, *roots_sources.snapshot.files),
            input_digest=input_digest,
            immutable_input_digests={immutable_input_key: ty_tool.digest},
            description=f"Run Ty on {pluralize(len(roots_sources.files), 'file')}.",
            level=LogLevel.DEBUG,
        ),
        **implicitly(),
    )

    return CheckResult.from_fallible_process_result(
        result,
        partition_description=partition.description(),
    )


@rule(
    desc="Determine if it is necessary to partition Ty's input (interpreter_constraints and resolves)",
    level=LogLevel.DEBUG,
)
async def ty_determine_partitions(
    request: TyRequest,
    ty: Ty,
    python_setup: PythonSetup,
) -> TyPartitions:
    resolve_and_interpreter_constraints_to_field_sets = (
        _partition_by_interpreter_constraints_and_resolve(request.field_sets, python_setup)
    )

    coarsened_targets = await resolve_coarsened_targets(
        CoarsenedTargetsRequest(field_set.address for field_set in request.field_sets),
        **implicitly(),
    )
    coarsened_targets_by_address = coarsened_targets.by_address()

    return TyPartitions(
        TyPartition(
            FrozenOrderedSet(field_sets),
            CoarsenedTargets(
                OrderedSet(
                    coarsened_targets_by_address[field_set.address] for field_set in field_sets
                )
            ),
            resolve if len(python_setup.resolves) > 1 else None,
            interpreter_constraints or ty.interpreter_constraints,
        )
        for (resolve, interpreter_constraints), field_sets in sorted(
            resolve_and_interpreter_constraints_to_field_sets.items()
        )
    )


@rule(desc="Typecheck using Ty", level=LogLevel.DEBUG)
async def ty_typecheck(
    request: TyRequest,
    ty: Ty,
    platform: Platform,
) -> CheckResults:
    if ty.skip:
        return CheckResults([], checker_name=request.tool_name)

    # Explicitly excluding `ty` as a function argument to `ty_determine_partitions` and `ty_typecheck_partition`
    # as it throws "TypeError: unhashable type: 'Ty'"
    partitions = await ty_determine_partitions(request, **implicitly())
    partitioned_results = await concurrently(
        ty_typecheck_partition(partition, **implicitly()) for partition in partitions
    )
    return CheckResults(
        partitioned_results,
        checker_name=request.tool_name,
    )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *config_files.rules(),
        *pex_from_targets.rules(),
        UnionRule(CheckRequest, TyRequest),
    )
