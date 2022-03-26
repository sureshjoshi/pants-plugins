from experimental.ansible.sources import (
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlayContext, AnsibleRoleSource,
    )
from pants.engine.target import COMMON_TARGET_FIELDS, Target


class AnsibleDeployment(Target):
    alias = "ansible_deployment"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsiblePlaybook,
        AnsiblePlayContext,
    )
    help = ""


class AnsibleRole(Target):
    alias = "ansible_role"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsibleRoleSource,
    )
    help = "An Ansible Role, see https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html"
