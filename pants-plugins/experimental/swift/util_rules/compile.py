from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from experimental.swift.subsystems.toolchain import SwiftToolchain
from experimental.swift.target_types import SwiftFieldSet, SwiftSourceField
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.process import FallibleProcessResult, Process
from pants.engine.rules import Get, Rule, collect_rules, rule
from pants.engine.target import SourcesField, Target
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TypecheckSwiftModuleRequest:
    name: str
    targets: Iterable[Target]


@dataclass(frozen=True)
class FallibleTypecheckedSwiftModule:
    name: str
    process_result: FallibleProcessResult


@dataclass(frozen=True)
class CompileSwiftSourceRequest:
    field_sets = (SwiftFieldSet,)


@rule(desc="Set up Swift typecheck request", level=LogLevel.DEBUG)
async def typecheck_swift_module(
    toolchain: SwiftToolchain, request: TypecheckSwiftModuleRequest
) -> FallibleTypecheckedSwiftModule:

    source_fields = [target.get(SourcesField) for target in request.targets]
    source_files = await Get(
        SourceFiles,
        SourceFilesRequest(source_fields, for_sources_types=(SwiftSourceField,)),
    )
    logger.warning(source_files)
    result = await Get(
        FallibleProcessResult,
        Process(
            argv=(
                toolchain.exe,
                "-typecheck",
                *source_files.files,
            ),
            input_digest=source_files.snapshot.digest,
            description=f"Typechecking swift module with {pluralize(len(source_files.files), 'file')}.",
            level=LogLevel.DEBUG,
        ),
    )
    logger.warning(result)
    return FallibleTypecheckedSwiftModule(request.name, result)


def rules() -> Iterable[Rule | UnionRule]:
    return collect_rules()
