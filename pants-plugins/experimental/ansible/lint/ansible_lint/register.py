# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

"""A formatter and linter forAnsible playbooks, roles and collections.
See https://ansible-lint.readthedocs.io/en/latest/ for details"""

from __future__ import annotations

from typing import Iterable

from experimental.ansible.lint.ansible_lint import rules as ansible_lint_rules
from experimental.ansible.lint.ansible_lint import skip_field, subsystem
from pants.engine.rules import Rule
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *ansible_lint_rules.rules(),
        *skip_field.rules(),
        *subsystem.rules(),
    )
