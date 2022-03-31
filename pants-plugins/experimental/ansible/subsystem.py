from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.engine.rules import collect_rules


class Ansible(PythonToolBase):
    options_scope = "ansible"
    help = """ """

    default_version = "ansible-core==2.12.4"
    default_main = ConsoleScript("ansible-playbook")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]


def rules():
    return collect_rules()
