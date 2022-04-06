from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.option.custom_types import shell_str


class AnsibleLint(PythonToolBase):
    options_scope = "ansible-lint"
    help = """ansible-lint linter for Ansible"""

    default_version = "ansible-lint~=5.3.2"
    default_extra_requirements = [
        "ansible==5.3.0",
    ]
    default_main = ConsoleScript("ansible-lint")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]

    @classmethod
    def register_options(cls, register):
        super().register_options(register)
        register(
            "--args",
            type=list,
            member_type=shell_str,
            help=(
                "Arguments to pass directly to ansible-lint, e.g."
                f"`--{cls.options_scope}-args='-f pep8'"
            ),
        )

    @property
    def args(self) -> tuple[str, ...]:
        return tuple(self.options.args)
