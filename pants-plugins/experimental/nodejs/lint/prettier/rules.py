from dataclasses import dataclass
import logging
from platform import node

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

from experimental.nodejs.lint.prettier.subsystem import Prettier
from experimental.nodejs.target_types import NodeSourceField
from experimental.nodejs.rules import DownloadedNpxTool, NpxToolRequest
from experimental.nodejs.subsystem import NpxToolBase

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PrettierFmtFieldSet(FieldSet):
    required_fields = (NodeSourceField,)

    sources: NodeSourceField


class PrettierFmtRequest(FmtRequest):
    field_set_type = PrettierFmtFieldSet
    name = Prettier.options_scope

@dataclass(frozen=True)
class SetupRequest:
    request: PrettierFmtRequest
    check_only: bool


@dataclass(frozen=True)
class Setup:
    process: Process
    original_digest: Digest

@rule(level=LogLevel.DEBUG)
async def setup_prettier(setup_request: SetupRequest, prettier: Prettier) -> Setup:
    prettier_tool = await Get(
        DownloadedNpxTool,
        NpxToolRequest,
        prettier.get_request()
    )

    source_files = await Get(
        SourceFiles,
        SourceFilesRequest(field_set.sources for field_set in setup_request.request.field_sets),
    )

    source_files_snapshot = (
        source_files.snapshot
        if setup_request.request.prior_formatter_result is None
        else setup_request.request.prior_formatter_result
    )

    input_digest = await Get(
        Digest,
        MergeDigests(
            (source_files_snapshot.digest, prettier_tool.digest)
        ),
    )
    
    argv = [
        *prettier_tool.exe.split(" "),
        "--check" if setup_request.check_only else "--write",
        *source_files_snapshot.files,
    ]

    process = Process(
        argv=argv,
        input_digest=input_digest,
        output_files=source_files_snapshot.files,
        description=f"Run prettier on {pluralize(len(source_files_snapshot.files), 'file')}.",
        level=LogLevel.DEBUG,
        env=prettier_tool.env,
    )
    return Setup(process=process, original_digest=source_files_snapshot.digest)

@rule(desc="Format with prettier")
async def prettier_fmt(request: PrettierFmtRequest, prettier: Prettier) -> FmtResult:
    # if prettier.skip:
    #     return FmtResult.skip(formatter_name=request.name)
    setup = await Get(Setup, SetupRequest(request, check_only=False))
    result = await Get(ProcessResult, Process, setup.process)
    return FmtResult.from_process_result(
        result, original_digest=setup.original_digest, formatter_name=request.name
    )

@rule(desc="Lint with prettier", level=LogLevel.DEBUG)
async def prettier_lint(request: PrettierFmtRequest, prettier: Prettier) -> LintResults:
    # if prettier.skip:
        # return LintResults([], linter_name=request.name)
    setup = await Get(Setup, SetupRequest(request, check_only=True))
    result = await Get(FallibleProcessResult, Process, setup.process)
    return LintResults(
        [LintResult.from_fallible_process_result(result, strip_chroot_path=True)],
        linter_name=request.name,
    )


def rules():
    return (
        *collect_rules(),
        UnionRule(FmtRequest, PrettierFmtRequest),
        UnionRule(LintTargetsRequest, PrettierFmtRequest),
    )