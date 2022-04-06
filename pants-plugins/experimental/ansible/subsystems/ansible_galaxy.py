from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.option.option_types import ArgsListOption, StrListOption, StrOption


class AnsibleGalaxy(PythonToolBase):
    options_scope = "ansible-galaxy"
    name = "Ansible Galaxy"
    help = """ """

    default_version = "ansible-core==2.12.4"
    default_main = ConsoleScript("ansible-galaxy")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]

    requirements = StrOption(
        "--requirements",
        default=None,
        help=(
            "A list of collections of the format 'my_namespace.my_collection' which will be "
            "installed via `ansible-galaxy collection install -r` from the Galaxy server"
        ),
    )

    collections = StrListOption(
        "--collections",
        help=(
            "A list of collections of the format 'my_namespace.my_collection' which will be "
            "installed via `ansible-galaxy collection install` from the Galaxy server"
        ),
    )

    collections_path = StrOption(
        "--collections-path", default="./collections", help=(""), advanced=True
    )

    args = ArgsListOption(example="--token API_KEY")
