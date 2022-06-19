from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import logging

from experimental.swift.subsystems.toolchain import SwiftToolchain, SwiftSubsystem
from experimental.swift.target_types import (
    SwiftFieldSet,
    SwiftGeneratorFieldSet,
)
from pants.engine.internals.selectors import Get
from pants.engine.process import FallibleProcessResult, Process
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.core.goals.check import CheckRequest, CheckResults
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.engine.process import FallibleProcessResult, Process
from pants.util.logging import LogLevel
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.rules import Get, MultiGet, Rule, collect_rules, rule
from pants.engine.target import CoarsenedTargets
from pants.util.strutil import pluralize
from pants.engine.engine_aware import EngineAwareParameter, EngineAwareReturnType
from pants.engine.target import Target, SourcesField
from experimental.swift.target_types import SwiftSourceField, SwiftGeneratorSourcesField

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
