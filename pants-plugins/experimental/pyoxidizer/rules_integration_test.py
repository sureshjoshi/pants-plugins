import logging
from textwrap import dedent

from experimental.pyoxidizer.subsystem import PyOxidizer, rules as subsystem_rules
from experimental.pyoxidizer.rules import rules as pyoxidizer_rules, PyOxidizerFieldSet
from experimental.pyoxidizer.target_types import PyOxidizerTarget
from pants.backend.python.macros.python_artifact import PythonArtifact
from pants.backend.python.target_types import (
    PythonDistribution,
    PythonSourcesGeneratorTarget,
)
from pants.backend.python.goals.publish import PublishPythonPackageRequest, rules
from pants.backend.python.util_rules import dists, pex_from_targets
from pants.core.goals.package import BuiltPackage
from pants.core.goals.publish import PublishPackages, PublishProcesses
from pants.core.util_rules import source_files
from pants.engine.addresses import Address
from pants.testutil.rule_runner import QueryRule, RuleRunner

import pytest


@pytest.fixture
def rule_runner() -> RuleRunner:
    return RuleRunner(
        preserve_tmpdirs=True,
        rules=[
            # *source_files.rules(),
            # *dists.rules(),
            *pyoxidizer_rules(),
            *subsystem_rules(),
            *pex_from_targets.rules(),
            QueryRule(PublishProcesses, [PublishPythonPackageRequest]),
            QueryRule(BuiltPackage, [PyOxidizer, PyOxidizerFieldSet]),
        ],
        target_types=[
            PythonSourcesGeneratorTarget,
            PythonDistribution,
            PyOxidizerTarget,
        ],
        objects={"python_artifact": PythonArtifact},
    )


def project_files(add_config: bool = False) -> dict[str, str]:
    return {
        "BUILD": dedent(
            f"""\
            python_sources(
                name="libtest"
            )
            python_distribution(
                name="test-dist",
                dependencies=[":libtest"],
                wheel=True,
                sdist=False,
                provides=python_artifact(
                    name="test-dist",
                    version="0.1.0",
                ),
            )
            pyoxidizer_binary(
                name="test-bin",
                entry_point="hellotest.main",
                dependencies=[":test-dist"],
            )
            """
        ),
        "hellotest/main.py": """print("hello test")""",
    }


def test_packaging_without_config(rule_runner: RuleRunner, caplog):
    caplog.set_level(logging.DEBUG)
    rule_runner.write_files(project_files())
    tgt = rule_runner.get_target(Address("", target_name="test-bin"))

    field_set = PyOxidizerFieldSet.create(tgt)

    # Without this, I get "Was not able to locate a Python interpreter to execute rule code"
    rule_runner.set_options([], env_inherit={"PATH"})
    result = rule_runner.request(BuiltPackage, [field_set])
    print(result)


# def test_packaging_with_config(rule_runner: RuleRunner):
#     rule_runner.write_files(project_files(add_config=True))
#     tgt = rule_runner.get_target(Address("", target_name="test-bin"))

#     field_set = PyOxidizerFieldSet.create(tgt)

#     # Without this, I get "Was not able to locate a Python interpreter to execute rule code"
#     rule_runner.set_options([], env_inherit={"PATH"})
#     result = rule_runner.request(BuiltPackage, [field_set])
#     print(result)
