from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    Dependencies,
    MultipleSourcesField,
    SingleSourceField,
    Target,
    TargetFilesGenerator,
)

class NodeSourceField(SingleSourceField):
    expected_file_extensions = (".js", ".ts",)


class NodeGeneratorSourcesField(MultipleSourcesField):
    expected_file_extensions = (".js", ".ts",)

class NodeSourceTarget(Target):
    alias = "node_source"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
        NodeSourceField,
    )
    help = "A single NodeJS source file containing application or library code."

class NodeSourcesGeneratorTarget(TargetFilesGenerator):
    alias = "node_sources"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        NodeGeneratorSourcesField,
    )
    generated_target_cls = NodeSourceTarget
    copied_fields = COMMON_TARGET_FIELDS
    moved_fields = (
        Dependencies,
    )
    help = "Generate a `node_source` target for each file in the `sources` field."
