import os
from typing import Iterable

from experimental.nodejs.subsystem import NpxToolBase
from pants.core.util_rules.config_files import ConfigFilesRequest


class Prettier(NpxToolBase):
    options_scope = "prettier"
    help = "The PrettierJS formatting tool."

    default_version = "prettier@2.6.0"

    def config_request(self, dirs: Iterable[str]) -> ConfigFilesRequest:
        """
        PrettierJS will use the closest configuration file to the file currently being formatted, so add all of them
        In the event of multiple configuration files, PretterJS has an order of precedence specified here:https://prettier.io/docs/en/configuration.html
        """

        config_files = (
            *[f"prettier.config{ext}" for ext in [".js", ".cjs"]],
            *[
                f".prettierrc{ext}"
                for ext in [
                    "",
                    ".json",
                    ".yml",
                    ".yaml",
                    ".json5",
                    ".js",
                    ".cjs",
                    ".toml",
                ]
            ],
        )
        check_existence = [
            os.path.join(d, file) for file in config_files for d in ("", *dirs)
        ]
        return ConfigFilesRequest(
            discovery=True,
            check_existence=check_existence,
        )
