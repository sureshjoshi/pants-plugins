from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    Dependencies,
    MultipleSourcesField,
    SingleSourceField,
    Target,
    TargetFilesGenerator,
)


class AnsibleSourceField(SingleSourceField):
    pass
    # expected_file_extensions = (
    # ".yml",
    # ".yaml",
    # )


class AnsibleGeneratorSourcesField(MultipleSourcesField):
    pass
    # expected_file_extensions = (
    # ".yml",
    #     # ".yaml",
    # )


class AnsibleSourceTarget(Target):
    alias = "ansible_source"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
        AnsibleSourceField,
    )
    help = "A single ansible source file containing tasks or support code."


class AnsibleSourcesGeneratorTarget(TargetFilesGenerator):
    alias = "ansible_sources"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleGeneratorSourcesField,
    )
    generated_target_cls = AnsibleSourceTarget
    copied_fields = COMMON_TARGET_FIELDS
    moved_fields = (Dependencies,)
    help = "Generate a `ansible_source` target for each file in the `sources` field."


class AnsibleDependenciesField(Dependencies):
    pass


class AnsiblePlaybook(SingleSourceField):
    alias = "playbook"
    default = "playbook.yml"
    help = (
        "The .yml file to use when running ansible-playbook.\n\n"
        "Path is relative to the BUILD file's directory, e.g. `playbook='playbook.yml'`."
    )


class AnsibleDeployment(Target):
    alias = "ansible_deployment"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        AnsibleDependenciesField,
        AnsiblePlaybook,
    )
    help = ""
