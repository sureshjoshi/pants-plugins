from __future__ import annotations

from collections.abc import Iterable

from experimental.ansible.deploy import rules as deploy_rules
from experimental.ansible.goals import tailor
from experimental.ansible.rules import rules as ansible_rules
from experimental.ansible.target_types import (
    AnsibleDeployment,
    AnsibleSourcesGeneratorTarget,
    AnsibleSourceTarget,
)
from pants.engine.rules import Rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *deploy_rules(),
        *ansible_rules(),
        *tailor.rules(),
    )


def target_types() -> Iterable[type[Target]]:
    return (
        AnsibleDeployment,
        AnsibleSourceTarget,
        AnsibleSourcesGeneratorTarget,
    )
