from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    Dependencies,
    MultipleSourcesField,
    SingleSourceField,
    Target,
    TargetFilesGenerator,
)

class CppSourceField(SingleSourceField):
    expected_file_extensions = (".cpp", ".h",)


class CppGeneratorSourcesField(MultipleSourcesField):
    expected_file_extensions = (".cpp", ".h",)

class CppSourceTarget(Target):
    alias = "cpp_source"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        Dependencies,
        CppSourceField,
    )
    help = "A single cpp source or header file containing application or library code."

class CppSourcesGeneratorTarget(TargetFilesGenerator):
    alias = "cpp_sources"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        CppGeneratorSourcesField,
    )
    generated_target_cls = CppSourceTarget
    copied_fields = COMMON_TARGET_FIELDS
    moved_fields = (
        Dependencies,
    )
    help = "Generate a `cpp_source` target for each file in the `sources` field."
