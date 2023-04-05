# Copyright 2022 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).
from __future__ import annotations

import textwrap
from typing import Iterable

from pants.core.util_rules.external_tool import UnknownVersion
from pants.engine.fs import DownloadFile, FileDigest
from pants.engine.platform import Platform
from pants.engine.rules import Rule, collect_rules
from pants.engine.unions import UnionRule
from pants.option.option_types import StrListOption, StrOption
from pants.option.subsystem import Subsystem
from pants.util.strutil import softwrap


# TODO: Isn't there a regular "SubsystemError?"
class PythonStandaloneInterpreterError(Exception):
    pass


class PythonStandaloneInterpreter(Subsystem):
    options_scope = "python-standalone"
    help = softwrap(
        """
        Self-contained, highly-portable Python distributions.

        See https://python-build-standalone.readthedocs.io/en/latest/index.html for more information.
        """
    )

    default_interpreter_version = "3.11.1"
    default_version = "20230116"
    default_known_versions = [
        "3.11.1|20230116|linux_arm64|debf15783bdcb5530504f533d33fda75a7b905cec5361ae8f33da5ba6599f8b4|25579178",
        "3.11.1|20230116|linux_x86_64|02a551fefab3750effd0e156c25446547c238688a32fabde2995c941c03a6423|29321007",
        "3.11.1|20230116|macos_arm64|4918cdf1cab742a90f85318f88b8122aeaa2d04705803c7b6e78e81a3dd40f80|18024309",
        "3.11.1|20230116|macos_x86_64|20a4203d069dc9b710f70b09e7da2ce6f473d6b1110f9535fb6f4c469ed54733|18042424",
    ]

    interpreter_version = StrOption(
        default=lambda cls: cls.default_interpreter_version,
        advanced=True,
        help=lambda cls: f"Use this interpreter version of {cls.options_scope}.",
    )

    version = StrOption(
        default=lambda cls: cls.default_version,
        advanced=True,
        help=lambda cls: f"Use this version of {cls.options_scope}.",
    )

    known_versions = StrListOption(
        default=lambda cls: cls.default_known_versions,
        advanced=True,
        help=textwrap.dedent(
            f"""
        Known versions to verify downloads against.

        Each element is a pipe-separated string of `interpreter_version|version|platform|sha256|length`, where:

            - `interpreter_version` is the Python version string (e.g. 3.9.15)
            - `version` is the release version string (e.g. 20221106)
            - `platform` is one of [{','.join(Platform.__members__.keys())}],
            - `sha256` is the 64-character hex representation of the expected sha256
            digest of the download file, as emitted by `shasum -a 256`
            - `length` is the expected length of the download file in bytes, as emitted by
            `wc -c`

        E.g., `3.9.15|20221106|macos_arm64|6d00f0f13a67a80469817e79ef0bd8886db51b0ca79997c071b2f41d28584d89|1167760`.

        Values are space-stripped, so pipes can be indented for readability if necessary.
        """
        ),
    )

    _url_template = "https://github.com/indygreg/python-build-standalone/releases/download/{version}/cpython-{interpreter_version}+{version}-{platform}-install_only.tar.gz"
    _url_platform_mapping = {
        "linux_arm64": "aarch64-unknown-linux-gnu",
        "linux_x86_64": "x86_64-unknown-linux-gnu",
        "macos_arm64": "aarch64-apple-darwin",
        "macos_x86_64": "x86_64-apple-darwin",
    }

    def generate_url(self, plat: Platform) -> str:
        platform = self._url_platform_mapping.get(plat.value, "")
        return self._url_template.format(
            interpreter_version=self.interpreter_version, version=self.version, platform=platform
        )

    # TODO: Maybe someday this will be an external tool - if we want to use it internally for validation/testing/etc?
    # def generate_exe(self, plat: Platform) -> str:
    # return super().generate_exe(plat)

    def get_request(self, plat: Platform) -> DownloadFile:
        for known_version in self.known_versions:
            interpreter_version, version, platform, sha256, filesize = [
                x.strip() for x in known_version.split("|")
            ]
            if (
                plat.value == platform
                and interpreter_version == self.interpreter_version
                and version == self.version
            ):
                digest = FileDigest(fingerprint=sha256, serialized_bytes_length=int(filesize))
                try:
                    url = self.generate_url(plat)
                    # exe = self.generate_exe(plat)
                except PythonStandaloneInterpreterError as e:
                    raise PythonStandaloneInterpreterError(
                        f"Couldn't find {self.options_scope} {self.interpreter_version}+{self.version} on {plat.value}"
                    ) from e
                return DownloadFile(url=url, expected_digest=digest)
        raise UnknownVersion(
            softwrap(
                f"""
                No known version of {self.options_scope} {self.interpreter_version}+{self.version} on {plat.value} found in {self.known_versions}
                """
            )
        )


def rules() -> Iterable[Rule | UnionRule]:
    return (
        *collect_rules(),
        *PythonStandaloneInterpreter.rules(),  # type: ignore[call-arg]
    )
