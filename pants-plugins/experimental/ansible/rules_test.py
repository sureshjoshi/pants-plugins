from typing import List, Sequence

import pytest
import toml
from experimental.ansible import deploy, rules
from experimental.ansible.deploy import DeployResults
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
from pants.core.goals.lint import LintResults
from pants.core.util_rules import external_tool, source_files
from pants.core.util_rules.source_files import SourceFiles, SourceFilesRequest
from pants.engine.rules import QueryRule
from pants.engine.target import Target
from pants.testutil.rule_runner import RuleRunner


@pytest.fixture()
def rule_runner() -> RuleRunner:
    return make_rule_runner()


def make_rule_runner() -> RuleRunner:

    rr = RuleRunner(
        target_types=(
            AnsibleDeployment,
            AnsibleRole,
            AnsibleCollection,
        ),
        rules=(
            *external_tool.rules(),
            *rules.rules(),
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
        """Check that check-mode just runs"""
        target = make_target(rule_runner, "helloansible", "helloansible")
        check_results = self.run_ansible_check(rule_runner, target)
        assert len(check_results) == 1
        assert check_results[0].stdout == "\nplaybook: helloansible/playbook.yml\n"

    @staticmethod
    def run_ansible_deploy(
        rule_runner: RuleRunner, target: Target
    ) -> Sequence[CheckResult]:
        check_results = rule_runner.request(
            DeployResults, (AnsibleFieldSet.create(target),)
        )
        return check_results.results

    def test_deploy_runs(self, rule_runner: RuleRunner):
        """Check that deployment runs"""
        target = make_target(rule_runner, "helloansible", "helloansible")
        deploy_results: DeployResults = self.run_ansible_deploy(rule_runner, target)
        assert len(deploy_results) == 1
        result = deploy_results[0]
        assert result.exit_code == 0
        print(result.stdout)
        assert (
            "localhost                  : ok=6    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0"
            in result.stdout
        ), "summary does not match expected output"

    def test_deploy_uses_args(self, rule_runner: RuleRunner):
        """
        Check that the extra args to ansible-playbook are passed

        We do this by adding `--tags hihello`, which targets 0 tasks,
        and then we check that no tasks ran.
        """
        target = make_target(rule_runner, "helloansible", "helloansible_with_tags")
        deploy_results: DeployResults = self.run_ansible_deploy(rule_runner, target)
        assert (
            "localhost                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0"
            in deploy_results[0].stdout
        )


class TestLint:
    ansible_lint_output = List[str]

    @staticmethod
    def run_ansible_lint(rule_runner: RuleRunner, target: Target) -> LintResults:
        field_sets = [AnsibleLintFieldSet.create(target)]
        lint_results = rule_runner.request(
            LintResults, [AnsibleLintRequest(field_sets)]
        )
        return lint_results.results

    @staticmethod
    def assert_ansible_lint_run(
        lint_results: LintResults, expected_exit_code=2
    ) -> ansible_lint_output:
        assert len(lint_results) == 1

        result = lint_results[0]
        assert result.exit_code == expected_exit_code

        stdout_lines = list(filter(bool, result.stdout.split("\n")))
        return stdout_lines

    def test_lint_deployment(self, rule_runner: RuleRunner):
        target = make_target(rule_runner, "helloansible", "helloansible")
        lint_results = self.run_ansible_lint(rule_runner, target)

        output = self.assert_ansible_lint_run(lint_results)
        assert len(output) == 2  # TODO: might change if ansible-lint changes

    def test_lint_collection(self, rule_runner: RuleRunner):
        target = make_target(
            rule_runner, "helloansible/hello/collection/", "hello.collection"
        )
        lint_results = self.run_ansible_lint(rule_runner, target)

        output = self.assert_ansible_lint_run(lint_results)
        assert len(output) == 8  # TODO: might change if ansible-lint changes

    def test_lint_role(self, rule_runner: RuleRunner):
        target = make_target(
            rule_runner,
            "helloansible/hello/collection/roles/hellorole",
            "helloansiblerole",
        )
        lint_results = self.run_ansible_lint(rule_runner, target)

        output = self.assert_ansible_lint_run(lint_results)
        assert len(output) == 6  # TODO: might change if ansible-lint changes

    def test_lint_args_used(self):
        """
        Test that the global args for ansible-lint are used

        We do this by shimming to use the `--version` argument,
        which spits out an entirely different output.
        """
        rule_runner = make_rule_runner()
        rule_runner.set_options(
            ["--ansible-lint-args='--version'"],
            env_inherit={"PATH"},
        )

        target = make_target(
            rule_runner,
            "helloansible/hello/collection/roles/hellorole",
            "helloansiblerole",
        )
        lint_results = self.run_ansible_lint(rule_runner, target)
        output = self.assert_ansible_lint_run(lint_results, 0)
        assert "ansible-lint" in output[0] and "using ansible" in output[0]
