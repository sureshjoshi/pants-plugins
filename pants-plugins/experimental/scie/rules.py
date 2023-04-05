# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Iterable

from experimental.scie.config import Boot, Command, File, Lift
from experimental.scie.subsystems.science import Science
from experimental.scie.target_types import (
    ScieBinaryNameField,
    ScieDependenciesField,
)
from experimental.scie.subsystems.standalone import PythonStandaloneInterpreter
from pants.core.goals.package import BuiltPackage, BuiltPackageArtifact, PackageFieldSet
from pants.core.goals.run import RunFieldSet, RunRequest, RunInSandboxBehavior
from pants.core.util_rules.external_tool import DownloadedExternalTool, ExternalToolRequest
from pants.engine.fs import (
    CreateDigest,
    Digest,
    DigestEntries,
    DownloadFile,
    FileContent,
    MergeDigests,
    Snapshot,
)
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessResult
from pants.engine.rules import Get, MultiGet, Rule, collect_rules, rule
from pants.engine.target import (
    DependenciesRequest,
    FieldSetsPerTarget,
    FieldSetsPerTargetRequest,
    Targets,
)
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel
from pants.backend.python.goals.package_pex_binary import rules as pex_binary_rules

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScieFieldSet(PackageFieldSet, RunFieldSet):
    required_fields = (ScieDependenciesField,)
    run_in_sandbox_behavior = RunInSandboxBehavior.RUN_REQUEST_HERMETIC

    binary_name: ScieBinaryNameField
    dependencies: ScieDependenciesField


@rule(level=LogLevel.DEBUG)
async def scie_jump_binary(
    science: Science,
    field_set: ScieFieldSet,
    standalone_interpreter: PythonStandaloneInterpreter,
    platform: Platform,
) -> BuiltPackage:
    # 1. Grab the dependencies of this target (start with 1 pex file)
    # 2. Get the interpreter_constraints for the Pex to determine which version of the Python Standalone to use
    # 3. Run science to generate the Scie Jump binaries (depending on the `platforms` setting)
    # 4. Profit?
    
    direct_deps = await Get(Targets, DependenciesRequest(field_set.dependencies))

    # deps_field_sets = await Get(
    #     FieldSetsPerTarget, FieldSetsPerTargetRequest(PackageFieldSet, direct_deps)
    # )
    # built_packages = await MultiGet(
    #     Get(BuiltPackage, PackageFieldSet, field_set) for field_set in deps_field_sets.field_sets
    # )

    # # Download the Scie Jump tool
    # downloaded_tool = await Get(
    #     DownloadedExternalTool, ExternalToolRequest, scie_jump.get_request(platform)
    # )

    # # Download the standalone python interpreter for this architecture
    # downloaded_interpreter = await Get(
    #     Digest, DownloadFile, standalone_interpreter.get_request(platform)
    # )
    # logger.error(downloaded_interpreter)

    # digest_entries = await Get(DigestEntries, Digest, downloaded_interpreter)
    # assert (
    #     len(digest_entries) == 1
    # ), "downloaded_interpreter should only contain a single compressed archive file"
    # downloaded_interpreter_filename = digest_entries[0].path

    # pex_name = built_packages[0].artifacts[0].relpath
    # assert pex_name is not None, "PEX dependency must exist"

    # binary_name = field_set.binary_name.value or field_set.address.target_name

    # # TODO: Config is going to be the trickiest part of scie-jump integration, at least until Lift
    # # For now, just creating a complicated example
    # lift_config = Lift(
    #     name=binary_name,
    #     description="Some generated field?",
    #     boot=Boot(
    #         commands={
    #             "": Command(
    #                 exe="{scie.bindings.venv}/venv/bin/python3.9",
    #                 args=["{scie.bindings.venv}/venv/pex"],
    #                 env={"=PATH": "{cpython}/python/bin:{scie.env.PATH}"},
    #                 description="My awesome tool",
    #             )
    #         },
    #         bindings={
    #             "venv": Command(
    #                 exe="{cpython}/python/bin/python3.9",
    #                 args=[
    #                     "{pexecutable}",
    #                     "venv",
    #                     "--bin-path",
    #                     "prepend",
    #                     "--compile",
    #                     "--rm",
    #                     "all",
    #                     "{scie.bindings}/venv",
    #                 ],
    #                 env={
    #                     "=PATH": "{cpython}/python/bin:{scie.env.PATH}",
    #                     "PEX_TOOLS": "1",
    #                     "PEX_ROOT": "{scie.bindings}/pex_root",
    #                 },
    #                 description="Installs Pants in a venv and pre-compiles .pyc.",
    #             )
    #         },
    #     ),
    #     files=[
    #         File(
    #             name=downloaded_interpreter_filename,
    #             key="cpython",
    #             # size=downloaded_interpreter.serialized_bytes_length,
    #             # hash=downloaded_interpreter.fingerprint
    #         ),
    #         File(name=pex_name, key="pexecutable"),
    #     ],
    # )

    # lift_file = await Get(
    #     Digest, CreateDigest([FileContent("lift.json", lift_config.to_json().encode("utf-8"))])
    # )
    # input_digest = await Get(
    #     Digest,
    #     MergeDigests(
    #         (
    #             downloaded_tool.digest,
    #             downloaded_interpreter,
    #             lift_file,
    #             *(built_package.digest for built_package in built_packages),
    #         )
    #     ),
    # )

    # process = Process(
    #     argv=(downloaded_tool.exe,),
    #     input_digest=input_digest,
    #     description="Run scie-jump on the input digests ",
    #     output_files=[binary_name],
    # )
    # result = await Get(ProcessResult, Process, process)
    # snapshot = await Get(
    #     Snapshot,
    #     Digest,
    #     result.output_digest,
    # )
    # return BuiltPackage(
    #     result.output_digest,
    #     artifacts=tuple(BuiltPackageArtifact(file) for file in snapshot.files),
    # )


@rule
async def run_scie_binary(field_set: ScieFieldSet) -> RunRequest:
    """After packaging, the scie-jump plugin will place the executable in a location like this:
    dist/{binary name}

    {binary name} will default to `target_name`, but can be modified on the `scie_binary` target.
    """

    binary = await Get(BuiltPackage, PackageFieldSet, field_set)
    assert len(binary.artifacts) == 1, "`scie_binary` should only generate one output package"
    artifact = binary.artifacts[0]
    assert artifact.relpath is not None
    return RunRequest(digest=binary.digest, args=(os.path.join("{chroot}", artifact.relpath),))


# @rule
# async def run_scie_debug_adapter_binary(
#     field_set: ScieFieldSet,
# ) -> RunDebugAdapterRequest:
#     raise NotImplementedError(
#         "Debugging a `scie_binary` using a debug adapter has not yet been implemented."
#     )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        UnionRule(PackageFieldSet, ScieFieldSet),
        # UnionRule(RunFieldSet, ScieFieldSet),
        *ScieFieldSet.rules(),
    )
