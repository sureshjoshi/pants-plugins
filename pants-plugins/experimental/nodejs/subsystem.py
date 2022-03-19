from pants.core.util_rules.external_tool import ExternalTool
from pants.engine.platform import Platform

class NodeJS(ExternalTool):
    options_scope = "nodejs"
    help = "The NodeJS Javascript runtime (including npm and npx)."

    default_version = "v16.14.1"
    default_known_versions = [
        "v16.14.1|macos_x86_64|af35abd727b051c8cdb8dcda9815ae93f96ef2c224d71f4ec52034a2ab5d8b61|30414480",
    ]

    def generate_url(self, plat: Platform) -> str:
        platform_mapping = {
            # "macos_arm64": "darwin.x86_64",
            "macos_x86_64": "darwin-x64",
            # "linux_arm64": "linux.aarch64",
            # "linux_x86_64": "linux.x86_64",
        }
        plat_str = platform_mapping[plat.value]
        return f"https://nodejs.org/dist/{self.version}/node-{self.version}-{plat_str}.tar.gz"

    def generate_exe(self, _: Platform) -> str:
        return f"./bin/node"

class Npx(ExternalTool):
    options_scope = "nodejs"
    help = "The NPX tool for NodeJS."


    default_version = "v17.7.1"
    default_known_versions = [
        "v17.7.1|macos_x86_64|94bfec7b7c034da3b626de77b9c8e6ba26418b160e805fc8a8106fbb0b797355|40556065",
    ]
    # default_version = "v16.14.1"
    # default_known_versions = [
    #     "v16.14.1|macos_x86_64|af35abd727b051c8cdb8dcda9815ae93f96ef2c224d71f4ec52034a2ab5d8b61|30414480",
    # ]

    def generate_url(self, plat: Platform) -> str:
        platform_mapping = {
            # "macos_arm64": "darwin.x86_64",
            "macos_x86_64": "darwin-x64",
            # "linux_arm64": "linux.aarch64",
            # "linux_x86_64": "linux.x86_64",
        }
        plat_str = platform_mapping[plat.value]
        return f"https://nodejs.org/dist/{self.version}/node-{self.version}-{plat_str}.tar.gz"

    def generate_exe(self, _: Platform) -> str:
        return f"./node-{self.version}-darwin-x64/bin/node"

