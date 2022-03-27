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
        check_existence = []
        for d in ("", *dirs):
            check_existence.append(os.path.join(d, ".clang-format"))

        return ConfigFilesRequest(
            specified=("hellocpp/.clang-format",)
            # check_existence=check_existence,
            # discovery=True
        )