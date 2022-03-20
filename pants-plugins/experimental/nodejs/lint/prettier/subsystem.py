from experimental.nodejs.subsystem import NpxToolBase


class Prettier(NpxToolBase):
    options_scope = "prettier"
    help = "The PrettierJS formatting tool."

    default_version = "prettier@2.6.0"
