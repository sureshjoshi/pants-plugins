from __future__ import annotations

from typing import Iterable

from experimental.ansible.deploy import rules as deploy_rules
from experimental.ansible.rules import rules as ansible_rules
from experimental.ansible.target_types import (
    AnsibleCollection,
    AnsibleDeployment,
    AnsibleRole,
)
from pants.engine.rules import Rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *deploy_rules(),
        *ansible_rules(),
    )


def target_types() -> Iterable[type[Target]]:
    return (AnsibleDeployment, AnsibleRole, AnsibleCollection)
