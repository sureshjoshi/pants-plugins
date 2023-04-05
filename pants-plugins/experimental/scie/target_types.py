# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from pants.core.goals.package import OutputPathField
from pants.engine.target import COMMON_TARGET_FIELDS, Dependencies, Target
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


class ScieTarget(Target):
    alias = "scie_binary"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        ScieDependenciesField,
        ScieBinaryNameField,
    )
    help = softwrap(
        """
        A single-file Python executable with a Python interpreter embedded, built via scie-jump.

        To use this target, first create a `pex_binary` target with the code you want included
        in your binary, per {doc_url('pex-files')}. Then add this `pex_binary` target to the
        `dependencies` field. See the `help` for `dependencies` for more information.
        """
    )
