from pants.engine.platform import Platform
from experimental.nodejs.subsystem import NodeJS

class Prettier(NodeJS):
    options_scope = "prettier"
    help = "The PrettierJS formatting tool."

    default_version = "2.6.0"

    def generate_exe(self, _: Platform) -> str:
        return f"./bin/node"

