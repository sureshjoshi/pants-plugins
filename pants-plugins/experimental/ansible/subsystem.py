from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.engine.rules import collect_rules


class Ansible(PythonToolBase):
    options_scope = "ansible"
    help = """ """

    default_version = "ansible==5.3.0"
    default_main = ConsoleScript("ansible-playbook")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]


class AnsibleLint(PythonToolBase):
    options_scope = "ansible-lint"
    help = """ansible-lint linter for Ansible"""

    default_version = "ansible-lint==5.4.0"
    default_extra_requirements = [
        "ansible==5.3.0"
    ]
    default_main = ConsoleScript("ansible-lint")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]


def rules():
    return collect_rules()
