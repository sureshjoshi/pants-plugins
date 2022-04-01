from pants.option.subsystem import Subsystem
from pants.option.option_types import StrListOption, StrOption, FileOption
from pants.backend.python.target_types import ConsoleScript
from pants.option.option_types import ArgsListOption

class AnsibleGalaxy(Subsystem):
    options_scope = "ansible-galaxy"
    name = "Ansible Galaxy"
    help = """ """

    default_main = ConsoleScript("ansible-galaxy")

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
        "--collections-path",
        default="./collections",
        help=(
            ""
        ),
        advanced=True
    )

    args = ArgsListOption(example="--token API_KEY")



    