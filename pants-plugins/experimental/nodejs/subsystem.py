from dataclasses import dataclass
from typing import ClassVar, Mapping

from pants.core.util_rules.external_tool import ExternalTool
from pants.engine.fs import Digest
from pants.engine.platform import Platform
from pants.option.subsystem import Subsystem


class NodeJS(ExternalTool):
    options_scope = "nodejs"
    help = "The NodeJS Javascript runtime (including npm and npx)."

    default_version = "v16.14.1"
    default_known_versions = [
        "v16.14.1|macos_arm64|8f6d45796f3d996484dcf53bb0e53cd019cd0ef7a1a247bd0178ebaa7e63a184|28983951",
        "v16.14.1|macos_x86_64|af35abd727b051c8cdb8dcda9815ae93f96ef2c224d71f4ec52034a2ab5d8b61|30414480",
        "v16.14.1|linux_arm64|53aeda7118cd1991424b457907790033326f432ee6c2908a7693920124622cf4|32852829",
        "v16.14.1|linux_x86_64|8db3d6d8ecfc2af932320fb12449de2b5b76f946ac72b47c6a9074afe82737ff|32861678",
    ]

    PLATFORM_MAPPING = {
        "macos_arm64": "darwin-arm64",
        "macos_x86_64": "darwin-x64",
        "linux_arm64": "linux-arm64",
        "linux_x86_64": "linux-x64",
    }

    def generate_url(self, plat: Platform) -> str:
        plat_str = self.PLATFORM_MAPPING[plat.value]
        return f"https://nodejs.org/dist/{self.version}/node-{self.version}-{plat_str}.tar.gz"

    def generate_exe(self, plat: Platform) -> str:
        plat_str = self.PLATFORM_MAPPING[plat.value]
        return f"./node-{self.version}-{plat_str}/bin/node"


@dataclass(frozen=True)
class NpxToolRequest:
    npm_package: str


@dataclass(frozen=True)
class DownloadedNpxTool:
    digest: Digest
    exe: str
    env: Mapping[str, str]


class NpxToolBase(Subsystem):
    default_version: ClassVar[str]

    def get_request(self) -> NpxToolRequest:
        return NpxToolRequest(self.default_version)
