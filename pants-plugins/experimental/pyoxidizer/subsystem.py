from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.engine.rules import collect_rules


class PyOxidizer(PythonToolBase):
    options_scope = "pyoxidizer"
    help = """The PyOxidizer utility for packaging Python code in a Rust binary (https://pyoxidizer.readthedocs.io/en/stable/pyoxidizer.html)."""

    default_version = "pyoxidizer==0.18.0"
    default_main = ConsoleScript("pyoxidizer")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.8"]


def rules():
    return (*collect_rules(),)
