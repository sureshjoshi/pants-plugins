from textwrap import dedent

from pants.backend.python.target_types import (
    PythonDistribution,
)
from pants.engine.target import (
    Target,
)


class MyPycPythonDistribution(Target):
    alias = "mypyc_python_distribution"
    core_fields = PythonDistribution.core_fields
    help = PythonDistribution.help
