from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    Dependencies,
    MultipleSourcesField,
    SingleSourceField,
    Target,
)


class AnsibleDependenciesField(Dependencies):
    pass


class AnsiblePlaybook(SingleSourceField):
    alias = "playbook"
    default = "playbook.yml"
    help = (
        "The .yml file to use when running ansible-playbook.\n\n"
        "Path is relative to the BUILD file's directory, e.g. `playbook='playbook.yml'`."
    )


class AnsiblePlayContext(MultipleSourcesField):
    alias = "ansiblecontext"
    default = (
        "*.yml",
        "*.ansible",
        "files/*",
        "tasks/*",
        "templates/*",
        "utils/*",
    )
    help = "Files reachable by an Ansible Play, such as tasks, templates, and files."


class AnsibleDeployment(Target):
    alias = "ansible_deployment"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsiblePlaybook,
        AnsiblePlayContext,
    )
    help = ""
