# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable

from experimental.ansible.target_types import (
    AnsibleSourcesGeneratorTarget,
    AnsibleSourceTarget,
)
from pants.engine.rules import Rule
from pants.engine.target import BoolField
from pants.engine.unions import UnionRule


class SkipAnsibleLintField(BoolField):
    alias = "skip_ansible_lint"
    default = False
    help = "If true, don't run ansible-lint on this target's code."


def rules() -> Iterable[Rule | UnionRule]:
    return (
        AnsibleSourceTarget.register_plugin_field(SkipAnsibleLintField),
        AnsibleSourcesGeneratorTarget.register_plugin_field(SkipAnsibleLintField),
    )
