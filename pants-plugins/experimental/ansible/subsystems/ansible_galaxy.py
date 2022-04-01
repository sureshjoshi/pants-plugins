from pants.option.subsystem import Subsystem
from pants.option.option_types import StrListOption, FileOption

class AnsibleGalaxy(Subsystem):
    options_scope = "ansible-galaxy"
    help = """ """

    requirements = FileOption(
        "--requirements",
        help=(
            "A list of collections of the format 'my_namespace.my_collection' which will be "
            "installed via `ansible-galaxy collection install` from the Galaxy server"
        ),
    )

    collections = StrListOption(
        "--collections",
        help=(
            "A list of collections of the format 'my_namespace.my_collection' which will be "
            "installed via `ansible-galaxy collection install` from the Galaxy server"
        ),
    )



    