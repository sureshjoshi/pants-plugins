# Copyright 2023 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import logging
import os
from dataclasses import asdict, dataclass
from typing import Iterable
from pathlib import PurePath

from pants.backend.python.target_types import PythonSourceField
from pants.backend.python.util_rules.pex_from_targets import InterpreterConstraintsRequest, interpreter_constraints_for_targets
from pants.core.target_types import EnvironmentAwarePackageRequest, RemovePrefix
from pants.init.plugin_resolver import InterpreterConstraints

from experimental.scie.config import Config, ScienceConfig, Interpreter, File, Command
from experimental.scie.subsystems.science import Science
from experimental.scie.target_types import (
    ScieBinaryNameField,
    ScieDependenciesField,
)
import toml
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
from pants.engine.fs import EMPTY_DIGEST
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
async def scie_binary(
    science: Science,
    field_set: ScieFieldSet,
    # standalone_interpreter: PythonStandaloneInterpreter,
    platform: Platform,
) -> BuiltPackage:
    # Grab the dependencies of this target, and build them
    direct_deps = await Get(Targets, DependenciesRequest(field_set.dependencies))
    deps_field_sets = await Get(
        FieldSetsPerTarget, FieldSetsPerTargetRequest(PackageFieldSet, direct_deps)
    )
    built_packages = await MultiGet(
        Get(BuiltPackage, EnvironmentAwarePackageRequest(field_set))
        for field_set in deps_field_sets.field_sets
    )
    logger.warning(built_packages)

    # Get the interpreter_constraints for the Pex to determine which version of the Python Standalone to use
    constraints = await Get(InterpreterConstraints, InterpreterConstraintsRequest([dep.address for dep in direct_deps]))
    # TODO: Pull the interpreter_universe from somewhere else (Python Build standalone?)
    minimum_version = constraints.minimum_python_version(["3.8", "3.9", "3.10", "3.11"])
    assert minimum_version is not None, "No minimum python version found"
    logger.warning(f"Minimum version: {minimum_version}, constraints: {constraints}")

    # TODO: These target platforms should be part of the target_type
    target_platforms = ["linux-x86_64", "macos-aarch64"]

    # Create a toml configuration from the input targets and the minimum_version
    interpreter = Interpreter(version=minimum_version)

    # Enumerate the files to add to the configuration
    artifact_names = [PurePath(artifact.relpath).name for built_pkg in built_packages for artifact in built_pkg.artifacts if artifact.relpath is not None]
    packagable_files = [File(name) for name in artifact_names]

    binary_name = field_set.binary_name.value or field_set.address.target_name

    # Create a toml configuration from the input targets and the minimum_version, and place that into a Digest for later usage
    config = Config(
        science=ScienceConfig(
            name=binary_name,
            description="My awesome tool",
            platforms=target_platforms,
            interpreters=[interpreter],
            files=packagable_files,
            commands=[Command(exe="#{cpython:python}", args=["{hellotyper-pex.pex}"])],
        )
    )
    logger.warning(config)
    config_filename = "config.toml"
    config_digest = await Get(Digest, CreateDigest([FileContent(config_filename, toml.dumps(asdict(config)).encode())]))

    # Download the Science tool for this platform
    downloaded_tool = await Get(
        DownloadedExternalTool, ExternalToolRequest, science.get_request(platform)
    )

    stripped_packages_digests = await MultiGet(
        Get(Digest, RemovePrefix(built_package.digest, "examples.python.hellotyper"))
        for built_package in built_packages
    )

    # Put the dependencies and toml configuration into a digest
    input_digest = await Get(
        Digest,
        MergeDigests(
            (
                config_digest,
                downloaded_tool.digest,
                *stripped_packages_digests,
            )
        ),
    )
    snapshot = await Get(
        Snapshot,
        Digest,
        input_digest,
    )
    logger.error(snapshot.files)

    # The output files are the binary name followed by each of the platforms
    output_files = [f"{binary_name}-{platform}" for platform in target_platforms]
    
    # Run science to generate the scie binaries (depending on the `platforms` setting)
    process = Process(
        argv=(downloaded_tool.exe, "build", config_filename),
        input_digest=input_digest,
        description="Run science on the input digests",
        output_files=output_files,
    )
    result = await Get(ProcessResult, Process, process)
    snapshot = await Get(
        Snapshot,
        Digest,
        result.output_digest,
    )
    logger.error(snapshot.files)
    return BuiltPackage(
        result.output_digest,
        artifacts=tuple(BuiltPackageArtifact(file) for file in snapshot.files),
    )

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
