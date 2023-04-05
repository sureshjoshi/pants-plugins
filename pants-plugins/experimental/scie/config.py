# Copyright 2023 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Config:
    science: ScienceConfig

@dataclass(frozen=True)
class ScienceConfig:
    name: str
    description: str
    platforms: Iterable[str]
    interpreters: Iterable[Interpreter] 
    files: Iterable[File]
    commands: Iterable[Command]

@dataclass(frozen=True)
class Interpreter:
    version: str
    id: str = "cpython"
    provider: str = "PythonBuildStandalone"
    lazy: bool = True

@dataclass(frozen=True)
class File:
    name: str

@dataclass(frozen=True)
class Command:
    exe: str
    args: Iterable[str]
