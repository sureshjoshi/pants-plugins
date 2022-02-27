from dataclasses import dataclass

from pants.backend.python.target_types import (
    GenerateSetupField,
    PythonDistributionEntryPointsField,
    PythonProvidesField,
    SDistConfigSettingsField,
    SDistField,
    WheelConfigSettingsField,
    WheelField,
)
from pants.engine.target import COMMON_TARGET_FIELDS, Dependencies, Target
from pants.util.docutil import doc_url


class MyPycPythonDistributionDependenciesField(Dependencies):
    supports_transitive_excludes = True


class MyPycPythonDistribution(Target):
    alias = "mypyc_python_distribution"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        MyPycPythonDistributionDependenciesField,
        PythonDistributionEntryPointsField,
        PythonProvidesField,
        GenerateSetupField,
        WheelField,
        SDistField,
        WheelConfigSettingsField,
        SDistConfigSettingsField,
    )
    help = (
        "A publishable Python setuptools distribution (e.g. an sdist or wheel).\n\nSee "
        f"{doc_url('python-distributions')}."
    )
