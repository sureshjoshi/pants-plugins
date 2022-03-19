from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript


class ClangFormat(PythonToolBase):
    options_scope = "clang-format"
    help = "The clang-format formatting tool."

    default_version = "clang-format==13.0.1"
    default_main = ConsoleScript("clang-format")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]
