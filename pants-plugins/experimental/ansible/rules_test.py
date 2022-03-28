from typing import Sequence

import pytest
import toml
from experimental.ansible import deploy, rules, subsystem
from experimental.ansible.rules import (
    AnsibleCheckRequest,
    AnsibleLintFieldSet,
    AnsibleLintRequest,
)
from experimental.ansible.sources import AnsibleFieldSet
from experimental.ansible.target_types import (
    AnsibleCollection,
    AnsibleDeployment,
    AnsibleRole,
)
from pants.backend.python.util_rules import pex
from pants.build_graph.address import Address
from pants.core.goals.check import CheckResult, CheckResults
from pants.core.goals.lint import LintResult, LintResults
from pants.core.util_rules import external_tool, source_files
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.rules import QueryRule
from pants.engine.target import Target
from pants.testutil.rule_runner import RuleRunner


@pytest.fixture()
def rule_runner() -> RuleRunner:
    rr = RuleRunner(
        target_types=(
            AnsibleDeployment,
            AnsibleRole,
            AnsibleCollection,
        ),
        rules=(
            *external_tool.rules(),
            *rules.rules(),
            *subsystem.rules(),
            *deploy.rules(),
            *source_files.rules(),
            *pex.rules(),
            QueryRule(CheckResults, (AnsibleCheckRequest,)),
            QueryRule(LintResults, (AnsibleLintRequest,)),
            QueryRule(SourceFiles, (SourceFilesRequest,)),
        ),
    )
    rr.set_options(
        [],
        env_inherit={"PATH"},
    )
    files = toml.load("pants-plugins/experimental/ansible/helloansible.test.toml")
    rr.write_files(files)
    return rr


def make_target(rule_runner: RuleRunner, address: str, target_name: str) -> Target:
    return rule_runner.get_target(Address(address, target_name=target_name))


class TestGeneral:
    def test_target(self, rule_runner: RuleRunner):
        target = make_target(rule_runner, "helloansible", "helloansible")
        assert target is not None
        assert isinstance(target, AnsibleDeployment)
        assert len(rule_runner.rules) > 0


class TestDeployment:
    @staticmethod
    def run_ansible_check(
        rule_runner: RuleRunner, target: Target
    ) -> Sequence[CheckResult]:
        field_sets = [AnsibleFieldSet.create(target)]
        check_results = rule_runner.request(
            CheckResults, [AnsibleCheckRequest(field_sets)]
        )
        return check_results.results

    def test_check_runs(self, rule_runner: RuleRunner):
        """Check that it just runs"""
        target = make_target(rule_runner, "helloansible", "helloansible")
        check_results = self.run_ansible_check(rule_runner, target)
        assert len(check_results) == 1
        assert check_results[0].stdout == "\nplaybook: helloansible/playbook.yml\n"


class TestLint:
    @staticmethod
    def run_ansible_lint(rule_runner: RuleRunner, target: Target) -> LintResults:
        field_sets = [AnsibleLintFieldSet.create(target)]
        lint_results = rule_runner.request(
            LintResults, [AnsibleLintRequest(field_sets)]
        )
        return lint_results.results

    def test_lint_deployment(self, rule_runner: RuleRunner):
        target = make_target(rule_runner, "helloansible", "helloansible")
        lint_results = self.run_ansible_lint(rule_runner, target)
        assert len(lint_results) == 1

        result = lint_results[0]
        assert result.exit_code == 2

        stdout_lines = list(filter(bool, result.stdout.split("\n")))
        assert len(stdout_lines) == 2  # TODO: might change if ansible-lint changes
