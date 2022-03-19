import logging
from dataclasses import dataclass

from experimental.cpp.lint.clangformat.subsystem import ClangFormat
from experimental.cpp.target_types import CppSourceField
from pants.backend.python.util_rules.pex import Pex, PexProcess, PexRequest
from pants.core.goals.fmt import FmtRequest, FmtResult
from pants.core.goals.lint import LintResult, LintResults, LintTargetsRequest
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.fs import Digest, MergeDigests
from pants.engine.internals.selectors import Get
from pants.engine.platform import Platform
from pants.engine.process import FallibleProcessResult, Process, ProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import FieldSet
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClangFormatFmtFieldSet(FieldSet):
    required_fields = (CppSourceField,)

    sources: CppSourceField


class ClangFormatRequest(FmtRequest):
    field_set_type = ClangFormatFmtFieldSet
    name = ClangFormat.options_scope


@dataclass(frozen=True)
class SetupRequest:
    request: ClangFormatRequest
    check_only: bool


@dataclass(frozen=True)
class Setup:
    process: Process
    original_digest: Digest


@rule(level=LogLevel.DEBUG)
async def setup_clangformat(
    setup_request: SetupRequest, clangformat: ClangFormat
) -> Setup:
    logger.debug("asdsadsd")
    clangformat_pex = await Get(
        Pex,
        PexRequest(
            output_filename="clangformat.pex",
            internal_only=True,
            requirements=clangformat.pex_requirements(),
            interpreter_constraints=clangformat.interpreter_constraints,
            main=clangformat.main,
        ),
    )

    source_files = await Get(
        SourceFiles,
        SourceFilesRequest(
            field_set.sources for field_set in setup_request.request.field_sets
        ),
    )

    source_files_snapshot = (
        source_files.snapshot
        if setup_request.request.prior_formatter_result is None
        else setup_request.request.prior_formatter_result
    )

    input_digest = await Get(
        Digest,
        MergeDigests([source_files_snapshot.digest, clangformat_pex.digest]),
    )

    argv = [
        "--Werror",
        "--dry-run" if setup_request.check_only else "-i",
        *source_files_snapshot.files,
    ]


    process = await Get (
        Process,
        PexProcess(
            clangformat_pex,
            argv=argv,
            description=f"Run clang-format on {pluralize(len(source_files_snapshot.files), 'file')}.",
            input_digest=input_digest,
            output_files=source_files_snapshot.files,
            level=LogLevel.DEBUG,
        )
    )

    return Setup(process=process, original_digest=source_files_snapshot.digest)


@rule(desc="Format with clang-format")
async def clangformat_fmt(
    request: ClangFormatRequest, clangformat: ClangFormat
) -> FmtResult:
    # if gofmt.skip:
    #     return FmtResult.skip(formatter_name=request.name)
    setup = await Get(Setup, SetupRequest(request, check_only=False))
    result = await Get(ProcessResult, Process, setup.process)
    return FmtResult.from_process_result(
        result, original_digest=setup.original_digest, formatter_name=request.name
    )


def rules():
    return (
        *collect_rules(),
        UnionRule(FmtRequest, ClangFormatRequest),
    )
