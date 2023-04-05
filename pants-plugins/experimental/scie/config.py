# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional

# FileType = Literal["zip", "tar", "tar.bz2", "tar.gz", "tar.xz", "tar.Z", "tar.zst", "blob", "directory"]


@dataclass(frozen=True)
class Command:
    exe: str
    args: list[str]
    env: dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None


@dataclass(frozen=True)
class Boot:
    commands: dict[str, Command]
    bindings: dict[str, Command] = field(default_factory=dict)


@dataclass(frozen=True)
class File:
    name: str
    key: str
    # TODO: asdict turns these into null values, which scie-jump doesn't like
    # TODO: Need to strip None's out
    # size: Optional[int] = None
    # hash: Optional[str] = None
    # file_type: Optional[str] = None


# Note: This is a placeholder config until the Lift tool is ready
@dataclass(frozen=True)
class Lift:
    name: str
    boot: Boot
    files: list[File]
    description: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(
            {"scie": {"lift": asdict(self)}},
            sort_keys=True,
            indent=2,
        )
