from experimental.ansible.deploy import rules as deploy_rules
from experimental.ansible.rules import rules as ansible_rules
from experimental.ansible.target_types import (
    AnsibleCollection,
    AnsibleDeployment,
    AnsibleRole,
)


def rules():
    return (
        *deploy_rules(),
        *ansible_rules(),
    )


def target_types():
    return (AnsibleDeployment, AnsibleRole, AnsibleCollection)
