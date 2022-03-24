from experimental.ansible.sources import (
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlayContext,
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
