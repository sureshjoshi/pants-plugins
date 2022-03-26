from experimental.ansible.deploy import rules as deploy_rules
from experimental.ansible.rules import rules as ansible_rules
from experimental.ansible.subsystem import rules as subsystem_rules
from experimental.ansible.target_types import AnsibleDeployment, AnsibleRole


def rules():
    return (
        *deploy_rules(),
        *ansible_rules(),
        *subsystem_rules(),
    )


def target_types():
    return (AnsibleDeployment, AnsibleRole)
