# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from experimental.pyoxidizer.rules import rules as pyoxidizer_rules
from experimental.pyoxidizer.target_types import PyOxidizerTarget


def rules():
    return [*pyoxidizer_rules()]


def target_types():
    return [PyOxidizerTarget]
