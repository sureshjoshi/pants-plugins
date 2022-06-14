from experimental.ansible.sources import (
    AnsibleCollectionSource,
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlaybookArgs,
    AnsiblePlayContext,
    AnsibleRoleSource,
)
from pants.engine.target import COMMON_TARGET_FIELDS, Target


class AnsibleDeployment(Target):
    alias = "ansible_deployment"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsiblePlaybook,
        AnsiblePlayContext,
        AnsiblePlaybookArgs,
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


class AnsibleCollection(Target):
    alias = "ansible_collection"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsibleCollectionSource,
    )
    help = "An Ansible Collection, see https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html"
