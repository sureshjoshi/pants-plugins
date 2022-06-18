from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from experimental.swift.subsystems.swiftc import Swiftc
from experimental.swift.target_types import (
    SwiftFieldSet,
    SwiftGeneratorFieldSet,
)
from pants.engine.internals.selectors import Get
from pants.engine.process import FallibleProcessResult, Process
from pants.engine.rules import Rule, collect_rules, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel


@dataclass(frozen=True)
class CompileSwiftSourceRequest:
    field_sets = (SwiftFieldSet, SwiftGeneratorFieldSet)


class FallibleBuiltSwiftModule:
    pass


@rule(desc="Compile with kotlinc")
async def compile_swift_source(
    swiftc: Swiftc,
    request: CompileSwiftSourceRequest,
) -> FallibleBuiltSwiftModule:

    process_result = await Get(
        FallibleProcessResult,
        Process(
            argv=[swiftc.path, *swiftc.args, *sources.snapshot.files],
            input_digest=sources_digest,
            output_files=(output_file,),
            description=f"Compile {request.component} with swiftc",
            level=LogLevel.DEBUG,
        ),
    )
    return FallibleBuiltSwiftModule()


def rules() -> Iterable[Rule | UnionRule]:
    return collect_rules()
