import os
from typing import Iterable

from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript
from pants.core.util_rules.config_files import ConfigFilesRequest


class ClangFormat(PythonToolBase):
    options_scope = "clang-format"
    help = "The clang-format formatting tool."

    default_version = "clang-format==13.0.1"
    default_main = ConsoleScript("clang-format")

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7"]

    def config_request(self, dirs: Iterable[str]) -> ConfigFilesRequest:
        """clang-format will use the closest configuration file to the file currently being formatted, so add all of them"""
        config_files = (
            ".clang-format",
            "_clang-format",
        )
        check_existence = [
            os.path.join(d, file) for file in config_files for d in ("", *dirs)
        ]
        return ConfigFilesRequest(
            discovery=True,
            check_existence=check_existence,
        )
