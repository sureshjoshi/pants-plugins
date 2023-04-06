# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations
from enum import Enum

from pants.core.goals.package import OutputPathField
from pants.engine.target import COMMON_TARGET_FIELDS, Dependencies, StringSequenceField, Target
from pants.util.strutil import softwrap


class ScieDependenciesField(Dependencies):
    required = True
    supports_transitive_excludes = True
    help = softwrap(
        """
        The address of a single `pex_binary` target to include in the binary, e.g.
        `['src/python/project:pex']`.
        """
    )

class ScieBinaryNameField(OutputPathField):
    alias = "binary_name"
    default = None
    help = softwrap(
        """
        The name of the binary that will be output by `scie-jump`. If not set, this will default
        to the name of this target.
        """
    )

class SciePlatform(Enum):
    LINUX_AARCH64 = "linux-aarch64"
    LINUX_X86_64 = "linux-x86_64"
    MACOS_AARCH64 = "macos-aarch64"
    MACOS_X86_64 = "macos-x86_64"


class SciePlatformField(StringSequenceField):
    alias = "platforms"
    default = None
    valid_choices = SciePlatform
    help = softwrap(
        """
        A field to indicate what what platform(s) to build for.

        The default selection is `None`, in which case we will default to the current platform.
        Possible values are: `linux-aarch64`, `linux-x86_64`, `macos-aarch64`, `macos-x86_64`.
        """
    )

class ScieTarget(Target):
    alias = "scie_binary"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        ScieDependenciesField,
        ScieBinaryNameField,
        SciePlatformField,
    )
    help = softwrap(
        """
        A single-file Python executable with a Python interpreter embedded, built via scie-jump.

        To use this target, first create a `pex_binary` target with the code you want included
        in your binary, per {doc_url('pex-files')}. Then add this `pex_binary` target to the
        `dependencies` field. See the `help` for `dependencies` for more information.
        """
    )
