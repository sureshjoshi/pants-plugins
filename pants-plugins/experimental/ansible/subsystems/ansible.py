from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.option.option_types import ArgsListOption


class Ansible(PythonToolBase):
    options_scope = "ansible"
    name = "Ansible"
    help = """ """

    default_version = "ansible-core==2.12.4"
    default_main = ConsoleScript("ansible-playbook")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]

    args = ArgsListOption(example="--ask-become-pass")
